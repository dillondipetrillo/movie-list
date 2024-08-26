from external_variables import DATABASE, EMAIL_PATTERN, ENTRY_FORM_FIELDS, FLASH_KEY, TMDB_API_KEY, PASSWORD_ERR, PASSWORD_PATTERN
from flask import flash, get_flashed_messages, jsonify, redirect, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import requests, sqlite3

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
        CREATE TABLE IF NOT EXISTS user_movies (
            user_id INTEGER,
            movie_id INTEGER,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    conn.commit()
    conn.close()


def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def is_logged_in(id):
    """Get the current user from the session id if user is present"""
    if not id: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE id = ?", (id,))
    user = cur.fetchone()
    user_dict = {
        "id": user[0],
        "username": user[1],
        "email": user[2],
    }
    conn.close()
    return user_dict


def create_form(form_type, form_title, form_button, form_action=None):
    """
        Creates a dictionary from the provided form info.
        Parameters:
        - form_type (str): builds form_fields based on type
        - form_title (str): for the title block and h1
        - form_action (str): if action is the same route as form, dont include
        - form_button (str): text for submit button
    """
    # Basic form dictionary with required fields
    form_info = {
        "form_type": form_type,
        "form_title": form_title,
        "form_button": form_button
    }

    # form_info["form_fields"] = [field.copy() for field in ENTRY_FORM_FIELDS[form_type]]
    form_info["form_fields"] = ENTRY_FORM_FIELDS[form_type]
    if form_action:
        form_info["form_action"] = form_action

    return form_info


def validate_form_data(form_data, form):
    """
        Loops over the form_data dictionary-like structure to
        validate each field. If any field is not validated then
        add error message to form dictionary
        Parameters:
        - form_data (dict-like): dict like structure of the submitted form data
        - form (dict): the current form dict
    """
    for field, value in form_data.items():
        # If there was an error validating, the error str will be returned
        is_not_valid = validate_form_field(form_data, field, form["form_type"])
        if is_not_valid:
            if "validate_errors" not in form:
                form["validate_errors"] = []
            form["validate_errors"].append({field: is_not_valid})
        if "values" not in form:
            form["values"] = []
        form["values"].append({field: value})

    # Form data is validated
    if "validate_errors" in form:
        return False
    return handle_valid_submission(form_data, form["form_type"])


def validate_form_field(form_data, form_field, type):
    """
        Get connect to database and validate the form field based on form type.
        If there is an error, return the error string, so it can be added to the
        forms error array. Otherwise return None
        Parameters:
        form_data (dict): dict like obect of submitted form data
        form_field (str): name of the form field being validated
        type (str): type of form
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Username field
    if form_field == "username":
        if len(form_data.get(form_field)) < 2:
            conn.close()
            return "Username must be at least 2 characters"
        cur.execute("SELECT * FROM users WHERE username = ?", (form_data.get(form_field),))
        user = cur.fetchone()
        if user:
            conn.close()
            return "Username already exists"

    # Email field
    elif form_field == "email" and not type == "reset":
        if not form_data.get(form_field) or not EMAIL_PATTERN.match(form_data.get(form_field)):
            conn.close()
            return "Not a valid email"
        # If it's the signup form, check that email is not in use
        cur.execute("SELECT * FROM users WHERE email = ?", (form_data.get(form_field),))
        user = cur.fetchone()
        if type == "signup":
            if user:
                conn.close()
                return "Email already in use"
        elif not user:
            conn.close()
            return "Email not found"

    # Password field
    elif form_field == "password":
        if type == "login" and form_data.get("email"):
            cur.execute("SELECT password_hash FROM users WHERE email = ?", (form_data.get("email"),))
            user = cur.fetchone()
            if user and not check_password_hash(user[0], form_data.get(form_field)):
                conn.close()
                return "Incorrect password"
        elif not form_data.get(form_field) or not PASSWORD_PATTERN.match(form_data.get(form_field)):
            conn.close()
            return PASSWORD_ERR
        # For reset password page, make sure new password is not the same as the old one
        if type == "reset" and form_data.get("password") and form_data.get("email"):
            cur.execute("SELECT password_hash FROM users WHERE email = ?", (form_data.get("email"),))
            user_pw = cur.fetchone()
            if check_password_hash(user_pw[0], form_data.get("password")):
                conn.close()
                return "The new password cannot be the same as a previously used password"

    # Confirm password field
    elif form_field == "password-confirm" and form_data.get("password"):
        if not form_data.get(form_field) or not form_data.get(form_field) == form_data.get("password"):
            conn.close()
            return "Passwords must match"

    # Close database connection
    conn.close()
    return


def handle_valid_submission(form_data, form_type):
    """
        Handles a valid form submission depending on form type
        Parameters:
        - form_data (dict): dict object of the submitted form data
        - form_type (str): type of form dict from list of forms
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # User attempting to login
    if form_type == "login":
        # Forget any user session data
        session.clear()
        # Get user_id and username
        cur.execute("SELECT id, username FROM users WHERE email = ?", (form_data.get("email"),))
        user = cur.fetchone()
        conn.close()
        session["user_id"] = user[0]
        session["username"] = user[1]
        # Keep user logged in for 30 days if checkbox is checked
        if form_data.get("stay-logged-in", None):
            session.permanent = True

    # User attempting to signup
    elif form_type == "signup":
        pw_hash = generate_password_hash(form_data.get("password"), method="pbkdf2", salt_length=16)
        cur.execute("""
            INSERT INTO users
            (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (form_data["username"], form_data.get("email"), pw_hash))
        # Get rows inserted
        if cur.rowcount < 1:
            conn.close()
            print("Error signing up user")
            return False
        conn.commit()
        cur.execute("SELECT id, username FROM users WHERE email = ?", (form_data.get("email"),))
        user = cur.fetchone()
        conn.close()
        session["user_id"] = user[0]
        session["username"] = user[1]

    # User is attempting to change passwords
    elif form_type == "reset":
        new_pw_hash = generate_password_hash(
            form_data.get("password"),
            method="pbkdf2",
            salt_length=16)
        cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_pw_hash, form_data.get("email")))
        conn.commit()
        conn.close()

    conn.close()
    return True


def save_movie(movie_id):
    """Saves movie to users list"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Get user id
    user_id = session.get("user_id")
    if not user_id:
        session[FLASH_KEY] = "danger"
        flash("Must be logged in to save movie.", session.get(FLASH_KEY))
        return

    # Check if movie is already saved
    cur.execute("SELECT * FROM user_movies WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    movie = cur.fetchone()
    if movie:
        session[FLASH_KEY] = "danger"
        flash("Movie already saved.", session.get(FLASH_KEY))
    else:
        # Insert movie into database
        cur.execute("INSERT INTO user_movies (user_id, movie_id) VALUES (?, ?)", (user_id, movie_id))
        conn.commit()
        session[FLASH_KEY] = "success"
        flash("Successfully saved movie!", session.get(FLASH_KEY))

    conn.close()


def search_query(query):
    """Makes call to api to get list of movies"""
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&include_adult=false&language=en-US&page=1")
    return jsonify(response.json())


def get_movie_info(id):
    """Returns individual movie info based on IMDB id"""
    response = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&include_adult=false&language=en-US")
    return response.json()


def get_movie_release_info(id):
    """
        Get release date info for individual movie based on IMDB id
        Only use US info
    """
    response = requests.get(f"https://api.themoviedb.org/3/movie/{id}/release_dates?api_key={TMDB_API_KEY}")
    return response.json()


def get_cast_info(id):
    """Get the cast list and director for movie"""
    response = requests.get(f"https://api.themoviedb.org/3/movie/{id}/credits?api_key={TMDB_API_KEY}&include_adult=false&language=en-US")
    return response.json()


def format_movie_info(movie_info, release_info, cast_info):
    """Creates dictionary for all required movie info"""
    # Build info that needs certain formatting, ex: rating, dates
    rating = release_year = release_date = country = runtime_str = percentage = circle_fill = None
    facts = []
    genres = []

    us_release_info = next((item for item in release_info["results"] if item["iso_3166_1"] == "US"), None)
    if us_release_info:
        us_data = us_release_info["release_dates"][1] if len(us_release_info["release_dates"]) > 1 else us_release_info["release_dates"][0]
        year = us_data["release_date"][:4]
        month = us_data["release_date"][5:7]
        day = us_data["release_date"][8:10]
        if us_data.get("certification"):
            rating = us_data.get("certification")
            facts.append(rating)
        release_year = year
        release_date = f"{month}/{day}/{year}"
        facts.append(release_date)
        country = us_release_info.get("iso_3166_1")
    else:
        release = movie_info.get("release_date")
        release_year = release[:4]
        year = release[:4]
        month = release[5:7]
        day = release[8:10]
        release_date = f"{month}/{day}/{year}"
        facts.append(release_date)

    # Get runtime in hours and minutes
    minutes = movie_info.get("runtime")
    hours = minutes // 60
    minutes = minutes % 60
    if hours > 0 and minutes > 0:
        runtime_str = f"{hours}h {minutes}m"
    elif hours > 0:
        runtime_str = f"{hours}h"
    else:
        runtime_str = f"{minutes}m"
    facts.append(runtime_str)

    # Build genres array
    if movie_info.get("genres"):
        for genre in movie_info.get("genres"):
            genres.append(genre.get("name"))

    # Get user vote percentage of movie
    percentage = int(movie_info.get("vote_average") * 10)
    circle_fill = int((percentage / 100) * 180)

    # Get director
    crew = cast_info.get("crew")
    director = next((person for person in crew if person.get("job") and person["job"] == "Director"), None)

    return {
        "title": movie_info.get("original_title", ''),
        "id": movie_info.get("id", ''),
        "poster": movie_info.get("poster_path", None),
        "genres": genres if genres else '',
        "facts": facts,
        "percentage": percentage,
        "vote_count": movie_info.get("vote_count"),
        "circle_fill": circle_fill if circle_fill else 0,
        "release_year": release_year if release_year else '',
        "country": country if country else '',
        "tagline": movie_info.get("tagline", ''),
        "overview": movie_info.get("overview", ''),
        "director": director.get("name", "Not listed"),
        "cast_list": cast_info.get("cast"),
    }