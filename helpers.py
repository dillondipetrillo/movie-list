import re, sqlite3

DATABASE = "movielist.db"
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
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
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    if result or not username:
        return "You must enter a unique username."
    
    # Verify email
    email = data["email"]
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = cur.fetchone()
    if result or not email or not EMAIL_PATTERN.match(email):
        return "You must enter a unique email. (example@mail.com)"
    
    # Verify password
    password = data["password"]
    if not PASSWORD_PATTERN.match(password) or not password:
        return "Password is must contain at least one uppercase letter, digit, and special character(@$!%*?&)."
    
    # Verify password confirmation
    confirm_password = data["confirm_password"]
    if not confirm_password == password or not confirm_password:
        return "Passwords must match."