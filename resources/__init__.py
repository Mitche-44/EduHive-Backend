from flask_restful import Api
from flask import Blueprint
from resources.auth import SignupResource, LoginResource, MeResource, ChangePasswordResource, LogoutResource
from resources.admin.users import ApproveUser

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(MeResource, '/me')
api.add_resource(ChangePasswordResource, '/change-password')
api.add_resource(LogoutResource, "/logout")

# Admin approving users
api.add_resource(ApproveUser, "/admin/users/<int:user_id>/approve")