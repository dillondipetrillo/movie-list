from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import create_tables, get_user_id, get_username, insert_user_db, login_required, verify_sign_up_data, verify_login_data
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
@login_required
def index():
    """Homepage for signed in user"""
    username = get_username(session["user_id"])
    return render_template("index.html", username=username[0])


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
            'confirm_password': request.form.get("password-confirm"),
        }
        # Set error message if cannot verify sign up form info
        error = verify_sign_up_data(sign_up_data)
        if error:
            return render_template("sign-up.html", error=error)
        
        pw_hash = generate_password_hash(
            sign_up_data["password"], 
            method="pbkdf2", 
            salt_length=16)
        # Insert the registered user into the database
        if not insert_user_db(sign_up_data, pw_hash):
            error = "Error adding user. Please try again."
            return render_template("sign-up.html", error=error)
        id = get_user_id(sign_up_data["username"])
        session["user_id"] = id[0]
        return redirect('/')
    else:
        return render_template("sign-up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for login page"""
    # Forget any user_id
    session.clear()
    
    # User is attempting to login
    if request.method == "POST":
        error = None
        sign_in_data = {
            'email': request.form.get("email"),
            'password': request.form.get("password"),
        }
        # Set error message if data cannot validate
        error = verify_login_data(sign_in_data)
        if error:
            return render_template("login.html", error=error)
        return redirect('/')
    
    # User reached via GET (clicking a link or via redirect)
    else:
        return render_template("login.html")