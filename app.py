from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from helpers import create_tables, get_user_id, insert_user_db, login_required, verify_sign_up_data, verify_login_data, get_user, search_query, verify_user_email
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash
import secrets, os

# Load env variables
load_dotenv()

# Configure application
app = Flask(__name__)

# Creates necessary tables for database
create_tables()

app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Configuration for Flask-Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def index():
    """Homepage for signed in user"""
    user = get_user(session.get("user_id", None))
    return render_template("index.html", user=user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new user"""
    # Redirect to home if already logged in
    if session.get("user_id"):
        return redirect("/")
    
    session.clear()
    
    if request.method == "POST":
        # Form submission
        errors = None
        sign_up_data = {
            'username': request.form.get("username"),
            'email': request.form.get("email"),
            'password': request.form.get("password"),
            'confirm_password': request.form.get("password-confirm"),
        }
        # Set error message if cannot verify sign up form info
        errors = verify_sign_up_data(sign_up_data)
        if errors:
            return render_template("signup.html", errors=errors, sign_up_info=sign_up_data, no_search=True)
        
        pw_hash = generate_password_hash(
            sign_up_data["password"], 
            method="pbkdf2", 
            salt_length=16)
        # Insert the registered user into the database
        if not insert_user_db(sign_up_data, pw_hash):
            error = "Error adding user. Please try again."
            return render_template("signup.html", error=error, no_search=True)
        id = get_user_id(sign_up_data["username"])
        session["user_id"] = id[0]
        session["username"] = sign_up_data["username"]
        return redirect('/')
    else:
        return render_template("signup.html", no_search=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for login page"""
    # Redirect to home if already logged in
    if session.get("user_id"):
        return redirect("/")
    
    # Forget any user_id
    session.clear()
    
    # User is attempting to login
    if request.method == "POST":
        error = None
        sign_in_data = {
            'email': request.form.get("email"),
            'password': request.form.get("password"),
            'stay-logged-in': request.form.get("stay-logged-in"),
        }
        # Set error message if data cannot validate
        error = verify_login_data(sign_in_data)
        if error:
            return render_template("login.html", error=error, sign_in_info=sign_in_data, no_search=True)
        return redirect('/')
    
    # User reached via GET (clicking a link or via redirect)
    else:
        return render_template("login.html", no_search=True)
    
    
@app.route("/logout")
def logout():
    """Logs the user out of their account"""
    # Forget any user id
    session.clear()
    
    # Redirect user to login
    return redirect('/')


@app.route("/results")
def results():
    """Calls the api to get movie search results"""
    query = request.args.get("q")
    if query:
        return search_query(query)
    
    
@app.route("/search")
def search():
    """Search results page"""
    query = request.args.get("q", "")
    return render_template("search.html", q=query)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Page to verify user in order to send url with token to change password"""
    email = request.form.get("email")
    if request.method == "POST":
        errors = verify_user_email(email)
        if errors:
            return render_template("reset-password.html", no_search=True, error=errors, email=email)
        else:
            token = s.dumps(email, salt="email-confirm")
            msg = Message("MovieList Password Reset Request", sender=os.getenv("EMAIL"), recipients=[email])
            link = url_for("reset_with_token", token=token, _external=True)
            msg.body = f"Your password reset link is {link}"
            try:
                mail.send(msg)
                return redirect(url_for("reset_password", success="Password reset link has been sent to your email"))
            except:
                return render_template("reset-password.html", no_search=True, email_error="Error sending email. Please try again.")
    else:
        success_msg = request.args.get("success")
        return render_template("reset-password.html", no_search=True, success=success_msg)
    

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    """Displays form for resetting password if token is not expired"""
    try:
        email = s.loads(token, salt="email-confirmation", max_age=900)
    except SignatureExpired:
        flash("The reset link has expired.", "error")
        return redirect("/reset-password")
    
    if request.method == "POST":
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")
        if new_password == confirm_password:
            flash("Your password has been updated successfully", "success")
            return redirect("/login")
        else:
            flash("Passwords do not match", "error")
    
    return render_template("reset-with-token.html", token=token)