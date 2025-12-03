from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, init_tasks_db, init_collaborations_db
from personal_tasks import personal_bp
from collaboration import collab_bp
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(personal_bp)
app.register_blueprint(collab_bp)

DB_NAME = "accounts.db"
TASK_DB = "todo.db"
COLLAB_DB = "collaborations.db"

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Session expired. Please log in again.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, post-check=0, pre-check=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.before_request
def check_sensitive_pages():
    sensitive_endpoints = ["edit_profile", "edit_password", "personal.profile"]
    if request.endpoint in sensitive_endpoints and "username" not in session:
        flash("Session expired. Please log in again.")
        return redirect(url_for("login"))

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    message = session.pop("message", None)
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()

        if row and check_password_hash(row[0], password):
            session["username"] = username
            return redirect(url_for("personal.profile"))
        else:
            error = "Invalid username or password."

    return render_template("accounts.html", error=error, message=message)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    error = None

    if request.method == "POST":
        full_name = request.form["fullName"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        security_question = request.form["securityQuestion"]

        if len(password) < 8:
            error = "Password must be at least 8 characters long."
            return render_template("register.html", message=message, error=error)
        if "@" not in email:
            error = "Please enter a valid email address."
            return render_template("register.html", message=message, error=error)

        hashed_password = generate_password_hash(password)
        hashed_security_question = generate_password_hash(security_question)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO accounts (full_name, email, username, password, security_question)
                    VALUES (?, ?, ?, ?, ?)
                """, (full_name, email, username, hashed_password, hashed_security_question))
                conn.commit()
            session["message"] = "Account created successfully! You can now log in."
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "Username or email already exists."

    return render_template("register.html", message=message, error=error)

@app.route("/editpassword", methods=["GET", "POST"])
@login_required
def edit_password():
    message = None
    error = None
    username = session["username"]

    if request.method == "POST":
        new_password = request.form["password"]
        if len(new_password) < 8:
            error = "Password must be at least 8 characters long."
            return render_template("editpassword.html", message=message, error=error)

        hashed_password = generate_password_hash(new_password)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET password = ? WHERE username = ?", (hashed_password, username))
            conn.commit()

        session.clear()
        session["message"] = "Password updated successfully! Please login again."
        return redirect(url_for("login"))

    return render_template("editpassword.html", username=username, message=message)

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        answer = request.form["securityQuestion"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT security_question FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()

        if not row:
            error = "User not found."
            return render_template("forgotpassword.html", error=error)

        if check_password_hash(row[0], answer):
            flash("Security answer correct. Please set your new password.")
            return redirect(url_for("edit_password"))
        else:
            error = "Wrong answer. Please try again."

    return render_template("forgotpassword.html", error=error)

@app.route("/editprofile", methods=["GET", "POST"])
@login_required
def edit_profile():
    message = None
    error = None
    username = session["username"]

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username = ?", (username,))
        user = cursor.fetchone()

    if not user:
        session.clear()
        flash("User not found.")
        return redirect(url_for("login"))

    user_data = {"full_name": user[0], "email": user[1], "username": user[2]}

    if request.method == "POST":
        new_name = request.form["fullName"]
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                if new_password.strip() == "":
                    cursor.execute("""
                        UPDATE accounts SET full_name=?, username=?, email=? WHERE username=?
                    """, (new_name, new_username, new_email, username))
                else:
                    if len(new_password) < 8:
                        error = "Password must be at least 8 characters long."
                        return render_template("editprofile.html", user=user_data, error=error, message=message)
                    hashed_password = generate_password_hash(new_password)
                    cursor.execute("""
                        UPDATE accounts SET full_name=?, username=?, email=?, password=? WHERE username=?
                    """, (new_name, new_username, new_email, hashed_password, username))
                conn.commit()

            session["username"] = new_username
            message = "Profile updated successfully!"
            user_data.update({"full_name": new_name, "email": new_email, "username": new_username})

        except sqlite3.IntegrityError:
            error = "Username or email already exists."

    return render_template("editprofile.html", user=user_data, error=error, message=message)

if __name__ == "__main__":
    init_db()
    init_tasks_db()
    init_collaborations_db()
    app.run(debug=True)
