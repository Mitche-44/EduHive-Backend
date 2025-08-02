import os
import requests as pyrequests 
from dotenv import load_dotenv
load_dotenv()

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)

from models.user import User
from extensions import db, blacklist
from utils.validators import validate_signup_data, validate_login_data
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


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
                password_hash=''
            )
            user.password = data["password"]

            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity={"id": user.id, "role": user.role})

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
            access_token = create_access_token(identity={"id": user.id, "role": user.role})
            return {"user": user.to_dict(), "access_token": access_token}, 200

        return {"message": "Invalid credentials"}, 401


class MeResource(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user_id = identity.get("id") if isinstance(identity, dict) else identity
        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        return user.to_dict(), 200


class ChangePasswordResource(Resource):
    @jwt_required()
    def put(self):
        identity = get_jwt_identity()
        user_id = identity.get("id") if isinstance(identity, dict) else identity
        user = User.query.get(user_id)

        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return {"message": "Current and new passwords are required."}, 400

        if not user or not user.check_password(current_password):
            return {"message": "Current password is incorrect."}, 401

        user.password = new_password
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
        code = data.get("code")

        if not code:
            return {"message": "Missing authorization code"}, 400

        try:
            # Exchange code for tokens
            token_response = pyrequests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": "postmessage",
                    "grant_type": "authorization_code"
                }
            )

            if token_response.status_code != 200:
                return {"message": "Failed to exchange code", "details": token_response.json()}, 400

            tokens = token_response.json()
            id_token_str = tokens.get("id_token")

            idinfo = id_token.verify_oauth2_token(id_token_str, grequests.Request(), GOOGLE_CLIENT_ID)

            google_id = idinfo["sub"]
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            user = User.query.filter_by(google_id=google_id).first()

            if not user and email:
                user = User.query.filter_by(email=email).first()
                if user:
                    user.google_id = google_id
                    db.session.commit()

            if not user:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    google_id=google_id,
                    password_hash='',
                    role="learner",
                    is_approved=True
                )
                db.session.add(user)
                db.session.commit()

            access_token = create_access_token(identity={"id": user.id, "role": user.role})
            return {"access_token": access_token, "user": user.to_dict()}, 200

        except Exception as e:
            return {"message": "Google login failed", "error": str(e)}, 400