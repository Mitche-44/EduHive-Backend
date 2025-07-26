
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.user import User
from extensions import db
from utils.validators import validate_signup_data, validate_login_data
from extensions import blacklist


class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        errors = validate_signup_data(data)
        if errors:
            return {"errors": errors}, 400

        try:
            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
            )
            user.password = data["password"]  # uses setter

            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            return {"user": user.to_dict(), "access_token": access_token}, 201

        except Exception as e:
            db.session.rollback()
            return {"message": "Signup failed", "error": str(e)}, 500


class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        errors = validate_login_data(data)
        if errors:
            return {"errors": errors}, 400

        user = User.query.filter_by(email=data["email"]).first()

        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user.id)
            return {"user": user.to_dict(), "access_token": access_token}, 200
        return {"message": "Invalid credentials"}, 401
    
class MeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404
        
        return user.to_dict(), 200
    
class ChangePasswordResource(Resource):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return {"message": "Current and new passwords are required."}, 400

        if not user or not user.check_password(current_password):
            return {"message": "Current password is incorrect."}, 401

        user.password = new_password  # Triggers setter to hash
        db.session.commit()

        return {"message": "Password updated successfully."}, 200

class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        return {"message": "Successfully logged out"}, 200
