from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from helpers import create_tables, get_user_id, insert_user_db, login_required, verify_sign_up_data, verify_login_data, get_user, search_query, verify_user_email, get_message_from_flash, verify_password_change, create_form, validate_form_data
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash
import secrets, os

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
    user = get_user(session.get("user_id", None))
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
    return render_template("entry-forms.html", no_search=True, form=form)


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
    return render_template("entry-forms.html", no_search=True, form=form)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Validate email to get password reset link"""
    form = create_form("forgot", "Confirm Email", "Send Reset Link")
    # Send reset password if email exists as user
    if request.method == "POST":
        # Submitted form data
        form_data = request.form
        validate_form_data(form_data, form)
    return render_template("entry-forms.html", no_search=True, form=form)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Reset Password form"""
    form = create_form("reset", "Reset Password", "Reset Password")
    # Reset password
    if request.method == "POST":
        # Submitted form data
        form_data = request.form
        validate_form_data(form_data, form)
    return render_template("entry-forms.html", no_search=True, form=form)


# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     """Register a new user"""
#     session.clear()
    
#     if request.method == "POST":
#         # Form submission
#         errors = None
#         sign_up_data = {
#             'username': request.form.get("username"),
#             'email': request.form.get("email"),
#             'password': request.form.get("password"),
#             'confirm_password': request.form.get("password-confirm"),
#         }
#         # Set error message if cannot verify sign up form info
#         errors = verify_sign_up_data(sign_up_data)
#         if errors:
#             return render_template("signup.html", errors=errors, sign_up_info=sign_up_data, no_search=True)
        
#         pw_hash = generate_password_hash(
#             sign_up_data["password"], 
#             method="pbkdf2", 
#             salt_length=16)
#         # Insert the registered user into the database
#         if not insert_user_db(sign_up_data, pw_hash):
#             error = "Error adding user. Please try again."
#             return render_template("signup.html", error=error, no_search=True)
#         id = get_user_id(sign_up_data["username"])
#         session["user_id"] = id[0]
#         session["username"] = sign_up_data["username"]
#         return redirect('/')

#     return render_template("signup.html", no_search=True)


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Route for login page"""
#     # User is attempting to login
#     if request.method == "POST":
#         # Forget any user_id
#         session.clear()
#         error = None
#         sign_in_data = {
#             'email': request.form.get("email"),
#             'password': request.form.get("password"),
#             'stay-logged-in': request.form.get("stay-logged-in"),
#         }
#         # Set error message if data cannot validate
#         error = verify_login_data(sign_in_data)
#         if error:
#             return render_template("login.html", error=error, sign_in_info=sign_in_data, no_search=True)
#         return redirect('/')

#     return render_template("login.html", no_search=True, reset_success=get_message_from_flash(session.pop(FLASH_KEY, None)))


@app.route("/logout")
def logout():
    """Logs the user out of their account and redirects to homepage"""
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


# @app.route("/reset-password", methods=["GET", "POST"])
# def reset_password():
#     """Page to verify user in order to send url with token to change password"""
#     email = request.form.get("email")
#     if request.method == "POST":
#         errors = verify_user_email(email)
#         if errors:
#             return render_template("reset-password.html", no_search=True, error=errors, email=email)
#         else:
#             token = s.dumps(email, salt="email-confirm")
#             msg = Message("MovieList Password Reset Request", sender=os.getenv("EMAIL"), recipients=[email])
#             link = url_for("reset_with_token", token=token, _external=True)
#             msg.body = f"Your password reset link is {link}"
#             try:
#                 mail.send(msg)
#                 session[FLASH_KEY] = "reset_success"
#                 flash("Password reset link has been sent to your email", session.get(FLASH_KEY))
#                 return redirect(url_for("login"))
#             except:
#                 return render_template("reset-password.html", no_search=True, email_error="Error sending email. Please try again.")

#     return render_template("reset-password.html", no_search=True, reset_error=get_message_from_flash(session.pop(FLASH_KEY, None)))


# @app.route("/reset-password/<token>", methods=["GET", "POST"])
# def reset_with_token(token):
#     """Displays form for resetting password if token is not expired"""
#     try:
#         email = s.loads(token, salt="email-confirm", max_age=900)
#     except SignatureExpired:
#         session[FLASH_KEY] = "reset_error"
#         flash("The reset link has expired. Please enter email again.", session.get(FLASH_KEY))
#         return redirect("/reset-password")
#     if request.method == "POST":
#         # try to update password
#         password_change_data = {
#             "email": email,
#             "password": request.form.get("password"),
#             "password-confirm": request.form.get("password-confirm"),
#         }
#         errors = verify_password_change(password_change_data)
#         if errors:
#             return render_template("reset-with-token.html", no_search=True, error=errors)
#         # Password verified, user is updated in db
#         session[FLASH_KEY] = "reset_true"
#         flash("Password has been successfully reset", session.get(FLASH_KEY))
#         return redirect("/login")

#     return render_template("reset-with-token.html", no_search=True, token=token)