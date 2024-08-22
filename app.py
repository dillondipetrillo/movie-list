from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from helpers import create_form, create_tables, format_movie_info, get_cast_info, get_movie_info, is_logged_in, login_required, get_movie_release_info, search_query, validate_form_data
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
import os, secrets

# Load env variables
load_dotenv()

# Configure application
app = Flask(__name__)

# Creates necessary tables for database
create_tables()

# Global variable for setting flash message key
FLASH_KEY = "flash_key" 

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

@app.before_request
def check_session():
    """Redirects logged in user to homepage if trying to visit pages 
        that should only be accessed by logged out users"""
    # public_routes = ["login", "signup", "reset_password", "reset_with_token"]
    public_routes = ["login", "signup", "forgot_password", "reset_password"]
    # Get current endpoint
    endpoint = request.endpoint
    
    # Check if user is logged in
    if session.get("user_id"):
        # Redirect to homepage if logged in user is trying to access route in public_routes
        if endpoint in public_routes:
            return redirect("/")


@app.route('/')
def index():
    """Homepage for signed in user"""
    user = is_logged_in(session.get("user_id", None))
    return render_template("index.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for login page"""
    form = create_form("login", "Login", "Login")
    # User login attempt
    if request.method == "POST":
        # Submitted form data
        form_data = request.form
        if validate_form_data(form_data, form):
            return redirect('/')
    return render_template("entry-forms.html", form=form, no_search=True)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new user if validated"""
    form = create_form("signup", "Sign Up", "Sign Up")
    # Sign up new user
    if request.method == "POST":
        # Submitted form data
        form_data = request.form
        if validate_form_data(form_data, form):
            return redirect('/')
    return render_template("entry-forms.html", form=form, no_search=True)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Validate email to get password reset link"""
    form = create_form("forgot", "Confirm Email", "Send Reset Link")
    # Send reset password if email exists as user
    if request.method == "POST":
        # Submitted form data
        form_data = request.form
        if validate_form_data(form_data, form):
            token = s.dumps(form_data["email"], salt="email-confirm")
            msg = Message("MovieList Password Reset Request", sender=os.getenv("EMAIL"), recipients=[form_data["email"]])
            link = url_for("reset_password", token=token, _external=True)
            msg.body = f"Your password reset link is {link}"
            try:
                mail.send(msg)
                session[FLASH_KEY] = "success"
                flash("Password reset link has been sent to your email", session.get(FLASH_KEY))
                return redirect(url_for("login"))
            except:
                session[FLASH_KEY] = "danger"
                flash("Error sending email. Please try again.", session.get(FLASH_KEY))

    return render_template("entry-forms.html", form=form, no_search=True)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset Password form"""
    try:
        email = s.loads(token, salt="email-confirm", max_age=900)
    except SignatureExpired:
        session[FLASH_KEY] = "danger"
        flash("The reset link has expired. Please enter email again.", session.get(FLASH_KEY))
        return redirect("/forgot-password")

    form = create_form("reset", "Reset Password", "Reset Password")
    # Reset password
    if request.method == "POST":
        # Submitted form data
        form_data = request.form.to_dict()
        form_data["email"] = email
        if validate_form_data(form_data, form):
            session[FLASH_KEY] = "success"
            flash("Password has been successfully reset", session.get(FLASH_KEY))
            return redirect("/login")

    return render_template("entry-forms.html", form=form, no_search=True, token=token)


@app.route("/logout")
def logout():
    """Logs the user out of their account and redirects to homepage"""
    # Forget any user id
    session.clear()
    # Redirect user to login
    return redirect('/')


@app.route("/movie")
def movie():
    """Page for individual movie information"""
    movie_id = request.args.get("id")
    movie_info = get_movie_info(movie_id)
    release_info = get_movie_release_info(movie_id)
    cast_info = get_cast_info(movie_id)
    formatted_movie_info = format_movie_info(movie_info, release_info, cast_info)
    return render_template("movie.html", movie=formatted_movie_info)


@app.route("/search-results")
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