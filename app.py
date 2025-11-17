from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, init_tasks_db, init_collaborations_db
from personal_tasks import personal_bp
from collaboration import collab_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register blueprints
app.register_blueprint(personal_bp)
app.register_blueprint(collab_bp)

# DB files
DB_NAME = "accounts.db"
TASK_DB = "tododatabase.db"
COLLAB_DB = "collaborations.db"

# --- ACCOUNT ROUTES ---
@app.route("/")
def home():
    return redirect("/login")

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
    session.pop("username", None)
    session["message"] = "Logged out successfully."
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

@app.route("/editpassword/<username>", methods=["GET", "POST"])
def edit_password(username):
    message = None
    error = None

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

        session["message"] = "Password updated successfully! You may login now."
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
            session["message"] = "Security answer correct. Please set your new password."
            return redirect(url_for("edit_password", username=username))
        else:
            error = "Wrong answer. Please try again."

    return render_template("forgotpassword.html", error=error)

@app.route("/editprofile/<username>", methods=["GET", "POST"])
def edit_profile(username):
    message = None
    error = None
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username = ?", (username,))
        user = cursor.fetchone()
    if not user:
        session["message"] = "User not found."
        return redirect(url_for("login"))

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
                        return render_template(
                            "editprofile.html",
                            user={"username": user[2], "email": user[1]},
                            error=error,
                            message=message
                        )

                    hashed_password = generate_password_hash(new_password)
                    cursor.execute("""
                        UPDATE accounts SET full_name=?, username=?, email=?, password=? WHERE username=?
                    """, (new_name, new_username, new_email, hashed_password, username))

                conn.commit()

            session["username"] = new_username
            session["message"] = "Profile updated successfully!"
            return redirect(url_for("personal.profile"))

        except sqlite3.IntegrityError:
            error = "Username or email already exists."

    return render_template("editprofile.html", user={"username": user[2], "email": user[1]}, error=error, message=message)

if __name__ == "__main__":
    init_db()
    init_tasks_db()
    init_collaborations_db()
    app.run(debug=True)