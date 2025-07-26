from flask_restful import Api
from flask import Blueprint
from .learner.badges import BadgeListResource, BadgeResource

api_bp = Blueprint("api", __name__)
api = Api(api_bp)



# Register endpoints
api.add_resource(BadgeListResource, "/badges")
api.add_resource(BadgeResource, "/badges/<int:badge_id>")