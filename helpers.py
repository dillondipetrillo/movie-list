import os, re, requests, sqlite3
from dotenv import load_dotenv
from flask import jsonify, redirect, session
from functools import wraps
from werkzeug.security import check_password_hash

# Load env variables
load_dotenv()

DATABASE = "movielist.db"
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
        Return error message if any fail.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify username
    username = data["username"]
    if not username:
        conn.close()
        return "You must enter a unique username."
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    if result:
        conn.close()
        return "Username already in use."
    
    # Verify email
    email = data["email"]
    if not email or not EMAIL_PATTERN.match(email):
        conn.close()
        return "You must enter a unique email. (example@mail.com)"
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = cur.fetchone()
    if result:
        conn.close()
        return "Email already in use."
    
    conn.close()
    # Verify password
    password = data["password"]
    if not PASSWORD_PATTERN.match(password) or not password:
        return "Password is must contain at least one uppercase letter, digit, and special character(@$!%*?&)."
    
    # Verify password confirmation
    confirm_password = data["confirm_password"]
    if not confirm_password == password or not confirm_password:
        return "Passwords must match."
   
    
def verify_login_data(data):
    """
        Verify the login username is present in database.
        Verify the login password is present and matches user
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify username
    email = data["email"]
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return "Email not found."
    
    conn.close()
    # Verify password matches
    password = data["password"]
    if not check_password_hash(user[3], password):
        return "Incorrect password."
    session["user_id"] = user[0]
    session["username"] = user[1]
    
    
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


def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def search_query(query):
    """Makes call to api to get list of movies."""
    response = requests.get(f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&type=movie&s={query}")
    return jsonify(response.json())


def movie_info(query):
    """Makes a call to api to get single movie info"""
    response = requests.get(f"")