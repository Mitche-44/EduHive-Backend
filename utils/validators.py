import re

def validate_signup_data(data):
    errors = {}

    if "first_name" not in data or not data["first_name"].isalpha():
        errors["first_name"] = "First name must be alphabetic."
    if "last_name" not in data or not data["last_name"].isalpha():
        errors["last_name"] = "Last name must be alphabetic."
    if "email" not in data or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        errors["email"] = "Invalid email format."
    if "password" not in data or len(data["password"]) < 6:
        errors["password"] = "Password must be at least 6 characters."

    return errors


def validate_login_data(data):
    errors = {}
    if "email" not in data:
        errors["email"] = "Email is required."
    if "password" not in data:
        errors["password"] = "Password is required."
    return errors
