# utils/decorators.py

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask import jsonify
from models.user import User

# Generic role-based decorator
def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return jsonify({"msg": "Access forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Decorator for checking if user is approved
def approved_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_approved:
            return jsonify({"msg": "Account not approved. Please wait for admin approval."}), 403
        return fn(*args, **kwargs)
    return wrapper

# Shortcuts for specific roles
learner_required = role_required("learner")
admin_required = role_required("admin")
contributor_required = role_required("contributor")
