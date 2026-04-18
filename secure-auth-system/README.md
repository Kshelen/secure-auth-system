# 🔐 Secure Authentication System

A full-stack secure login and registration system built with Python Flask, JWT authentication, and bcrypt password hashing.

## ✨ Features

- ✅ User Registration with input validation
- ✅ Secure Login with bcrypt password hashing
- ✅ JWT-based session management (2-hour expiry)
- ✅ Login history / audit logs with IP tracking
- ✅ Protected dashboard route (requires valid token)
- ✅ SQLite database for users and logs
- ✅ Password strength indicator on registration
- ✅ Clean, modern dark UI

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python + Flask | Backend web framework |
| bcrypt | Secure password hashing |
| PyJWT | JSON Web Token authentication |
| SQLite | Lightweight database |
| HTML/CSS/JavaScript | Frontend |

## 📁 Project Structure

```
secure-auth-system/
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── users.db             # SQLite database (auto-created)
└── templates/
    ├── login.html       # Login page
    ├── register.html    # Registration page
    └── dashboard.html   # Protected dashboard
```

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/secure-auth-system.git
cd secure-auth-system
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open your browser
```
http://127.0.0.1:5000
```

## 🔒 Security Features

- **bcrypt hashing**: Passwords are never stored in plain text
- **JWT tokens**: Stateless authentication with expiry
- **Input validation**: Server-side checks on all inputs
- **Login audit logs**: Every login attempt (success/fail) is recorded with IP address

## 📸 Screenshots

| Page | Description |
|---|---|
| `/login` | Login page with animated UI |
| `/register` | Registration with password strength meter |
| `/dashboard` | Protected user dashboard with login history |

---

Built as part of the Codec Technologies Internship Projects.
