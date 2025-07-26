from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Badge

# ✅ Fixed: Use "winners" instead of "winner_list" for frontend compatibility
def to_dict(badge):
    return {
        "id": badge.id,
        "title": badge.title,
        "awarded": badge.awarded,
        "winners": badge.winner_list(),  # ✅ now matches frontend expectation
        "image_url": badge.image_url
    }

class BadgeListResource(Resource):
    def get(self):
        badges = Badge.query.all()
        return [to_dict(b) for b in badges], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get("title")
        awarded = data.get("awarded", 0)
        winners = data.get("winners", "")
        image_url = data.get("image_url")

        if not title or not image_url:
            return {"error": "Title and image_url are required."}, 400

        badge = Badge(
            title=title,
            awarded=awarded,
            winners=winners,
            image_url=image_url
        )
        db.session.add(badge)
        db.session.commit()

        return to_dict(badge), 201

class BadgeResource(Resource):
    def get(self, badge_id):
        badge = Badge.query.get_or_404(badge_id)
        return to_dict(badge), 200

    @jwt_required()
    def patch(self, badge_id):
        badge = Badge.query.get_or_404(badge_id)
        data = request.get_json()

        badge.title = data.get("title", badge.title)
        badge.awarded = data.get("awarded", badge.awarded)
        badge.winners = data.get("winners", badge.winners)
        badge.image_url = data.get("image_url", badge.image_url)

        db.session.commit()
        return to_dict(badge), 200

    @jwt_required()
    def delete(self, badge_id):
        badge = Badge.query.get_or_404(badge_id)
        db.session.delete(badge)
        db.session.commit()
        return {"message": "Badge deleted successfully."}, 200
