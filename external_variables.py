from dotenv import load_dotenv
import os, re

load_dotenv()

# Regex pattern for simple email matching
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+$"
)

# Regex pattern for simple password matching
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{7,}$"
)

# Database name from environment variable
DATABASE = os.getenv("DATABASE_NAME")

# API key from environment variable
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# String for error for not matching password requirements
PASSWORD_ERR = "Password must be at least 7 characters and contain at least one uppercase letter, digit, and special character(@$!%*?&)."

# Global variable for setting flash message key
FLASH_KEY = "flash_key" 

################## Form Fields Start ##################
username_field = {
    "name": "username",
    "type": "text",
    "placeholder": "Username",
    "label": "Username",
}

email_field = {
    "name": "email",
    "type": "email",
    "placeholder": "Email",
    "label": "Email",
}
password_field = {
    "name": "password",
    "type": "password",
    "placeholder": "Password",
    "label": "Password",
}
new_password_field = {
    "name": "password",
    "type": "password",
    "placeholder": "New Password",
    "label": "New Password",
}

confirm_password_field = {
    "name": "password-confirm",
    "type": "password",
    "placeholder": "Confirm Password",
    "label": "Confirm Password",
}
################## Form Fields End ##################

# Possible form fields for each entry-form type
ENTRY_FORM_FIELDS = {
    "signup": [username_field, email_field, password_field, confirm_password_field],
    "login": [email_field, password_field],
    "forgot": [email_field],
    "reset": [new_password_field, confirm_password_field],
}