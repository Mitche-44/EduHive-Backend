from flask_restful import Api
from flask import Blueprint
from .learner.badges import BadgeListResource, BadgeResource
from resources.auth import SignupResource, LoginResource, MeResource, ChangePasswordResource, LogoutResource
from resources.admin.users import ApproveUser


api_bp = Blueprint("api", __name__)
api = Api(api_bp)




# Register endpoints
api.add_resource(BadgeListResource, "/badges")
api.add_resource(BadgeResource, "/badges/<int:badge_id>")

api.add_resource(SignupResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(MeResource, '/me')
api.add_resource(ChangePasswordResource, '/change-password')
api.add_resource(LogoutResource, "/logout")

# Admin approving users
api.add_resource(ApproveUser, "/admin/users/<int:user_id>/approve")

