from flask import Blueprint
from flask_restful import Api
from .payment import Payment


# Create main API blueprint
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Import your resources here when you create them
# from .user_resources import UserResource
# api.add_resource(UserResource, '/users')
# Import all models here

# Make them available when importing from models
__all__ = ['Payment']