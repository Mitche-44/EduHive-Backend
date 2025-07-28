
import os
from dotenv import load_dotenv
load_dotenv()
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.user import User
from extensions import db
from utils.validators import validate_signup_data, validate_login_data
from extensions import blacklist
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


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
    

class GoogleLogin(Resource):
    def post(self):
        data = request.json
        token = data.get("id_token")

        if not token:
            return {"message": "Missing ID token"}, 400

        try:
            # ✅ Verify token
            idinfo = id_token.verify_oauth2_token(token, grequests.Request(), GOOGLE_CLIENT_ID)

            google_id = idinfo["sub"]
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            # ✅ Step 1: Try find user by google_id
            user = User.query.filter_by(google_id=google_id).first()

            if user:
                # ✅ Found: Log them in
                access_token = create_access_token(identity=user.id)
                return {"access_token": access_token, "user": user.to_dict()}, 200

            # ✅ Step 2: Try find by email (existing non-Google user trying Google login)
            if not user and email:
                user = User.query.filter_by(email=email).first()

            if user:
                # ✅ Upgrade existing user to have google_id
                user.google_id = google_id
                db.session.commit()

                access_token = create_access_token(identity=user.id)
                return {"access_token": access_token, "user": user.to_dict()}, 200

            # ✅ Step 3: Register new Google user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                google_id=google_id,
                password_hash='',  # No password for Google
                role="learner",
                is_approved=True
            )
            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token, "user": user.to_dict()}, 201

        except ValueError as e:
            return {"message": "Invalid token", "error": str(e)}, 400


