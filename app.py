from flask import Flask, render_template, request, session
from flask_session import Session
from helpers import  create_tables

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
        error = None
        if not request.form.get("username"):
            error = "Username is required."
        elif not request.form.get("email"):
            error = "Email is required."
        elif not request.form.get("password"):
            error = "Password is required."
        elif not request.form.get("password-confirm"):
            error = "Confirm Password is required."
        else:
            # Handle successful form submission
            return
        return render_template("sign-up.html", error=error)
    else:
        return render_template("sign-up.html")
        