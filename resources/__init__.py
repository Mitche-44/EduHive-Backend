from flask_restful import Api
from flask import Blueprint

# Existing imports
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

# Quiz imports - Add these to your existing imports section
from resources.learner.quizzes import (
    QuizzesListResource,
    QuizDetailResource,
    QuizAttemptResource,
    QuizSubmissionResource,
    QuizResultResource,
    UserQuizStatsResource
)
from resources.contributor.quizzes import (
    ContributorQuizzesResource,
    ContributorQuizDetailResource,
    QuizQuestionsResource,
    QuizQuestionDetailResource,
    QuizAnalyticsResource
)
from resources.admin.quizzes import (
    AdminQuizzesOverviewResource,
    AdminQuizzesListResource,
    AdminQuizDetailResource,
    AdminQuizAttemptsResource,
    AdminQuizReportsResource
)

# Create API blueprints
api_bp = Blueprint("api", __name__)
api = Api(api_bp)

# Create separate blueprints for different user types
learner_bp = Blueprint("learner_api", __name__)
learner_api = Api(learner_bp)

contributor_bp = Blueprint("contributor_api", __name__)
contributor_api = Api(contributor_bp)

admin_bp = Blueprint("admin_api", __name__)
admin_api = Api(admin_bp)

# ============================================================================
# EXISTING ROUTES (unchanged)
# ============================================================================

# Register existing endpoints
api.add_resource(BadgeListResource, "/badges")
api.add_resource(BadgeResource, "/badges/<int:badge_id>")
api.add_resource(SignupResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(MeResource, '/me')
api.add_resource(ChangePasswordResource, '/change-password')
api.add_resource(LogoutResource, "/logout")

# Register existing blueprints
api_bp.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")  # Register the leaderboard blueprint
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

# ============================================================================
# NEW QUIZ ROUTES
# ============================================================================

# Learner quiz routes
learner_api.add_resource(QuizzesListResource, '/quizzes')
learner_api.add_resource(QuizDetailResource, '/quizzes/<string:quiz_id>')
learner_api.add_resource(QuizAttemptResource, '/quizzes/<string:quiz_id>/attempt')
learner_api.add_resource(QuizSubmissionResource, '/quizzes/<string:quiz_id>/attempts/<int:attempt_id>/submit')
learner_api.add_resource(QuizResultResource, '/quizzes/<string:quiz_id>/attempts/<int:attempt_id>/result')
learner_api.add_resource(UserQuizStatsResource, '/quiz-stats')

# Contributor quiz routes
contributor_api.add_resource(ContributorQuizzesResource, '/quizzes')
contributor_api.add_resource(ContributorQuizDetailResource, '/quizzes/<string:quiz_id>')
contributor_api.add_resource(QuizQuestionsResource, '/quizzes/<string:quiz_id>/questions')
contributor_api.add_resource(QuizQuestionDetailResource, '/quizzes/<string:quiz_id>/questions/<int:question_id>')
contributor_api.add_resource(QuizAnalyticsResource, '/quizzes/<string:quiz_id>/analytics')

# Admin quiz routes
admin_api.add_resource(AdminQuizzesOverviewResource, '/quiz-overview')
admin_api.add_resource(AdminQuizzesListResource, '/quizzes')
admin_api.add_resource(AdminQuizDetailResource, '/quizzes/<string:quiz_id>')
admin_api.add_resource(AdminQuizAttemptsResource, '/quizzes/<string:quiz_id>/attempts')
admin_api.add_resource(AdminQuizReportsResource, '/quiz-reports')

# Register the new API blueprints with the main blueprint
api_bp.register_blueprint(learner_bp, url_prefix="/learner")
api_bp.register_blueprint(contributor_bp, url_prefix="/contributor")
api_bp.register_blueprint(admin_bp, url_prefix="/admin")

# Import your resources here when you create them
# from .user_resources import UserResource
# api.add_resource(UserResourc