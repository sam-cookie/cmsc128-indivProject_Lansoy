from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/login")
def login():
    return render_template("accounts.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/forgotpassword")
def forgot_password():
    return render_template("forgotPassword.html")
