from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import create_tables, get_user_id, insert_user_db, login_required, verify_sign_up_data, verify_login_data, get_user, search_query
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
            return render_template("signup.html", error=error)
        
        pw_hash = generate_password_hash(
            sign_up_data["password"], 
            method="pbkdf2", 
            salt_length=16)
        # Insert the registered user into the database
        if not insert_user_db(sign_up_data, pw_hash):
            error = "Error adding user. Please try again."
            return render_template("signup.html", error=error, is_login=True)
        id = get_user_id(sign_up_data["username"])
        session["user_id"] = id[0]
        session["username"] = sign_up_data["username"]
        return redirect('/')
    else:
        return render_template("signup.html", is_login=True)


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
        }
        # Set error message if data cannot validate
        error = verify_login_data(sign_in_data)
        if error:
            return render_template("login.html", error=error, is_login=True)
        return redirect('/')
    
    # User reached via GET (clicking a link or via redirect)
    else:
        return render_template("login.html", is_login=True)
    
    
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
    
    
@app.route("/search", methods=["GET", "POST"])
def search():
    """Search results page"""
    if request.method == "GET":
        query = request.args.get("q")
    elif request.method == "POST":
        query = request.form.get("q")
    return render_template("search.html", q=query)