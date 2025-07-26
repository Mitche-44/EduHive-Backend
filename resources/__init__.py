from flask_restful import Api
from flask import Blueprint

api_bp = Blueprint("api", __name__)
api = Api(api_bp)



# Import your resources here when you create them
# from .user_resources import UserResource
# api.add_resource(UserResource, '/users')