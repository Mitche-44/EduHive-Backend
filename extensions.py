from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager
from models.user import User

jwt = JWTManager()
blacklist = set()  # This will store blacklisted tokens


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()


# check if id is blacklisted
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

#RBAC
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    user = User.query.get(identity)
    return {
        "role": user.role,
        "email": user.email
    }

# Use it in a protected route
# class AdminDashboard(Resource):
#     @jwt_required()
#     @role_required("admin")
#     def get(self):
#         return {"message": "Welcome to the admin dashboard"}

