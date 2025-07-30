import re

def is_valid_url(url):
    url_regex = re.compile(
        r'^(https?://)?'                   # Optional scheme
        r'([a-zA-Z0-9.-]+)'                # Domain
        r'(\.[a-zA-Z]{2,6})'               # TLD
        r'(/[a-zA-Z0-9&%_.\-/]*)?$'        # Path
    )
    return re.match(url_regex, url)

def validate_module_data(data):
    errors = {}

    # Title
    if not data.get("title") or len(data["title"].strip()) < 3:
        errors["title"] = "Title is required and must be at least 3 characters long."

    # Description
    if not data.get("description") or len(data["description"].strip()) < 10:
        errors["description"] = "Description is required and must be at least 10 characters long."

    # Content
    if "content" in data and not isinstance(data["content"], str):
        errors["content"] = "Content must be a string."

    # Media URL
    if data.get("media_url") and not is_valid_url(data["media_url"]):
        errors["media_url"] = "Media URL must be a valid URL."

    # Status
    if data.get("status") and data["status"] not in ["pending", "approved"]:
        errors["status"] = "Status must be either 'pending' or 'approved'."

    # Contributor ID
    if "contributor_id" not in data:
        errors["contributor_id"] = "Contributor ID is required."

    return errors


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


