from flask import Flask, render_template, request, session
from flask_session import Session
from helpers import create_tables, verify_sign_up_data

# Configure application
app = Flask(__name__)

# Creates necessary tables for database
create_tables()

# Configure session to user filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    """Register a new user"""
    if request.method == "POST":
        # Form submission
        error = None
        sign_up_data = {
            'username': request.form.get("username"),
            'email': request.form.get("email"),
            'password': request.form.get("password"),
            'confirm_password': request.form.get("password-confirm")
        }
        # Set error message if cannot verify sign up form info
        error = verify_sign_up_data(sign_up_data)
        if error:
            return render_template("sign-up.html", error=error)
        return render_template("sign-up.html")
    else:
        return render_template("sign-up.html")
        