from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import bcrypt
import jwt
import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
JWT_SECRET = "your_jwt_secret_key_change_in_production"
DATABASE = "users.db"

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                ip_address TEXT
            )
        """)
        conn.commit()

# ─── JWT Helper ───────────────────────────────────────────────────────────────

def generate_token(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get("token")
        if not token:
            return redirect(url_for("login_page"))
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            session.clear()
            return redirect(url_for("login_page"))
        except jwt.InvalidTokenError:
            session.clear()
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# ─── Routes: Pages ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    if session.get("token"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
@token_required
def dashboard():
    user = request.user
    with get_db() as conn:
        logs = conn.execute(
            "SELECT * FROM login_logs WHERE username = ? ORDER BY login_time DESC LIMIT 10",
            (user["username"],)
        ).fetchall()
        user_data = conn.execute(
            "SELECT username, email, created_at FROM users WHERE id = ?",
            (user["user_id"],)
        ).fetchone()
    return render_template("dashboard.html", user=user_data, logs=logs)

# ─── Routes: API ──────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed.decode("utf-8"))
            )
            conn.commit()
        return jsonify({"success": True, "message": "Account created successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username or email already exists."}), 409

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    ip = request.remote_addr

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            token = generate_token(user["id"], user["username"])
            session["token"] = token
            conn.execute(
                "INSERT INTO login_logs (user_id, username, status, ip_address) VALUES (?, ?, ?, ?)",
                (user["id"], username, "SUCCESS", ip)
            )
            conn.commit()
            return jsonify({"success": True, "message": "Login successful!"})
        else:
            if user:
                conn.execute(
                    "INSERT INTO login_logs (user_id, username, status, ip_address) VALUES (?, ?, ?, ?)",
                    (user["id"], username, "FAILED", ip)
                )
                conn.commit()
            return jsonify({"success": False, "message": "Invalid username or password."}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
