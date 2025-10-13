from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  

DB_NAME = "accounts.db"

@app.route("/")
def home():
    return redirect("/login")

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
        print("Database created successfully.")
    else:
        print("Database already exists.")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()

        if row and check_password_hash(row[0], password):
            flash("Login successful!", "success")
            return redirect(url_for("profile", username=username))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("accounts.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["fullName"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO accounts (full_name, email, username, password)
                    VALUES (?, ?, ?, ?)
                """, (full_name, email, username, hashed_password))
                conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
            row = cursor.fetchone()

        if row:
            flash("If this email exists, a reset link will be sent soon.", "info")
        else:
            flash("If this email exists, a reset link will be sent soon.", "info")

        #placeholder for senfing mail
        return redirect(url_for("login"))

    return render_template("forgotpassword.html")


@app.route("/profile/<username>")
def profile(username):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username = ?", (username,))
        user = cursor.fetchone()
    if user:
        return f"<h2>Welcome, {user[0]}!</h2><p>Username: {user[2]}<br>Email: {user[1]}</p>"
    else:
        return "User not found."


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
