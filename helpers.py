import os, re, requests, sqlite3
from dotenv import load_dotenv
from flask import get_flashed_messages, jsonify, redirect, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# Load env variables
load_dotenv()

# Global variables
DATABASE = os.getenv("DATABASE_NAME")
# Get API key
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
# Regex pattern for simple email matching
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+$"
)
# Regex pattern for simple password matching
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{7,}$"
)
PASSWORD_ERR = "Password must be at least 7 characters and contain at least one uppercase letter, digit, and special character(@$!%*?&)."

def get_db_connection():
    """
        Establish connection for database.
        Making the connection visible in multiple threads.
    """
    conn = sqlite3.connect(DATABASE)
    return conn


def create_tables():
    """
        Creates a new database table for users, movies, and combined.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            year INTEGER
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_movies (
            user_id INTEGER,
            movie_id INTEGER,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        );
    """)

    conn.commit()
    conn.close()


def verify_sign_up_data(data):
    """
        Verify the sign up form username is present and unique.
        Verify the sign up form email is present and unique and a valid email address.
        Verify that the sign up form password is present and valid compared to regex pattern.
        Verify that the confirm_password matches the password.
        Return error messages dictionary if any fail.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Variable to hold dictionary of error messages if any errors found
    error_msgs = {}

    # Verify username
    username = data["username"]
    if not username or len(username) < 2:
        error_msgs["username"] = "Username must be at least 2 characters"
    else:
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cur.fetchone()
        if result:
            error_msgs["username"] = "Username already exists"

    # Verify email
    email = data["email"]
    if not email or not EMAIL_PATTERN.match(email):
        error_msgs["email"] = "Enter a valid email (example@mail.com)"
    else:
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cur.fetchone()
        if result:
            error_msgs["email"] = "Email already exists"

    # Verify password
    password = data["password"]
    if not PASSWORD_PATTERN.match(password) or not password:
        error_msgs["password"] = PASSWORD_ERR

    # Verify password confirmation
    confirm_password = data["confirm_password"]
    if not confirm_password == password or not confirm_password:
        error_msgs["confirm_password"] = "Passwords must match."

    conn.close()
    return error_msgs


def verify_login_data(data):
    """
        Verify the login username is present in database.
        Verify the login password is present and matches user
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Variable to hold the dictionary of possible error messages
    error_msgs = {}

    # Verify username
    email = data["email"]
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if not email or not EMAIL_PATTERN.match(email):
        error_msgs["email"] = "Not a valid email"
        conn.close()
        return error_msgs
    elif not user:
        conn.close()
        error_msgs["email"] = "Email not found"
        return error_msgs

    conn.close()
    # Verify password matches
    password = data["password"]
    if not check_password_hash(user[3], password):
        error_msgs["password"] = "Incorrect password."
        return error_msgs
    session["user_id"] = user[0]
    session["username"] = user[1]
    persist_login = data["stay-logged-in"]
    # Keep user logged in for 30 days if checkbox is checked
    if persist_login:
        session.permanent = True
    return None


def insert_user_db(user_data, pw_hash):
    """Insert the registering user into the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO users 
                (username, email, password_hash)
                VALUES (?, ?, ?)""", 
                (user_data["username"], user_data["email"], pw_hash))
    # Get rows inserted
    rows_inserted = cur.rowcount
    if rows_inserted < 1:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True


def get_user_id(username):
    """Get the id of the username registered"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    id = cur.fetchone()
    conn.close()
    return id


def get_user(user_id):
    """Get the current user from the session id if user is present"""
    if not user_id: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    user_dict = {
        "id": user[0],
        "username": user[1],
        "email": user[2],
    }
    conn.close()
    return user_dict


def verify_user_email(email):
    """Returns an empty error dictionary if email is in db
        otherwise return the error message in the dictionary"""
    err_msgs = {}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,))
    user_email = cur.fetchone()
    conn.close()
    if not EMAIL_PATTERN.match(email):
        err_msgs["email"] = "Not a valid email"
    elif not user_email:
        err_msgs["email"] = "No email found"
    return err_msgs


def verify_password_change(user_data):
    """Verify password change data. Confirms password matches password
        requirements and matches with the confirm password field.
        If so, users password is updated"""
    # Verify password and password-confirm
    password = user_data["password"]
    password_confirm = user_data["password-confirm"]
    if not PASSWORD_PATTERN.match(password) or not password:
         return PASSWORD_ERR
    if not password == password_confirm:
        return "Passwords must match"

    # Validate that the new password is not same as the current password
    email = user_data["email"]
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    user_pw = cur.fetchone()
    if check_password_hash(user_pw[0], password):
        conn.close()
        return "The new password cannot be the same as a previously used password"

    # Password is valid and matches the password-confirm field and is unique
    new_pw_hash = generate_password_hash(
        password, 
        method="pbkdf2", 
        salt_length=16)
    cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_pw_hash, email))
    conn.commit()
    conn.close()
    return None


def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_message_from_flash(category):
    """Gets the message from flash in the provided category"""
    if not category: return None
    messages = get_flashed_messages(with_categories=True)
    cat_msg = [msg for cat, msg in messages if cat == category]
    return cat_msg[0] if cat_msg else None


def search_query(query):
    """Makes call to api to get list of movies."""
    response = requests.get(f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&type=movie&s={query}")
    return jsonify(response.json())