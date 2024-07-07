from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import create_tables, insert_user_db, verify_sign_up_data
from werkzeug.security import generate_password_hash

# Configure application
app = Flask(__name__)

# Creates necessary tables for database
create_tables()

# Configure session to user filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    """Homepage for signed in user"""
    return render_template("index.html")

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    """Register a new user"""
    session.clear()
    
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
        
        pw_hash = generate_password_hash(sign_up_data["password"], method="pbkdf2", salt_length=16)
        # Insert the registered user into the database
        if not insert_user_db(sign_up_data, pw_hash):
            error = "Error adding user. Please try again."
            return render_template("sign-up.html", error=error)
        return redirect('/')
    else:
        return render_template("sign-up.html")
        