from flask_restful import Api
from flask import Blueprint
from resources.learner.badges import BadgeListResource, BadgeResource
from resources.auth import SignupResource, LoginResource, MeResource, ChangePasswordResource, LogoutResource
from resources.admin.users import ApproveUser

from resources.auth import GoogleLogin
from resources.contributor.modules import ContributorModuleListResource, ContributorModuleResource

from resources.learner.leaderboard import leaderboard_bp
from resources.public.newsletter import newsletter_bp
# from resources.learner.subscriptions import subscription_bp
from resources.public.testimonial import testimonial_bp
from resources.admin.testimonial_admin import admin_testimonial_bp
from resources.admin.subscriptions import admin_subscriptions_bp
from resources.admin.admin_leaderboard import admin_leaderboard_bp
from resources.admin.testimonial_admin import admin_testimonial_bp
from resources.admin.subscriptions import admin_subscriptions_bp
from resources.admin.admin_leaderboard import admin_leaderboard_bp






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

api_bp.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")# Register the leaderboard blueprint
api_bp.register_blueprint(newsletter_bp, url_prefix="/newsletter")  # Register the newsletter blueprint
# api_bp.register_blueprint(subscription_bp, url_prefix="/subscription")  # Register the subscription blueprint
api_bp.register_blueprint(admin_subscriptions_bp, url_prefix="/admin/subscriptions")  # Register the admin subscriptions blueprint
api_bp.register_blueprint(admin_leaderboard_bp, url_prefix="/admin/leaderboard")  # Register the admin leaderboard blueprint
api_bp.register_blueprint(testimonial_bp, url_prefix="/testimonials")  # Register the testimonial blueprint



api_bp.register_blueprint(admin_testimonial_bp, url_prefix="/admin/testimonials")  # Register the admin testimonial blueprint



# Admin approving users
api.add_resource(ApproveUser, "/admin/users/<int:user_id>/approve")


api.add_resource(GoogleLogin, "/auth/google-login")

# contributor modules
api.add_resource(ContributorModuleListResource, "/contributor/modules")
api.add_resource(ContributorModuleResource, "/contributor/modules/<int:module_id>")
=======



# Import your resources here when you create them
# from .user_resources import UserResource
# api.add_resource(UserResource, '/users')

