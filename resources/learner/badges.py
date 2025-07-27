from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from extensions import db
from models import Badge


def serialize_badge(badge):
    return {
        "id": badge.id,
        "title": badge.title,
        "awarded": badge.awarded,
        "winners": badge.winner_list,  # Use the property
        "image_url": badge.image_url
    }


class BadgeListResource(Resource):
    def get(self):
        try:
            badges = Badge.query.all()
            return [serialize_badge(badge) for badge in badges], 200
        except Exception as e:
            return {"message": "Failed to fetch badges", "error": str(e)}, 500

    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get("title")
        awarded = data.get("awarded", 0)
        winners = data.get("winners", "")
        image_url = data.get("image_url")

        if not title or not image_url:
            return {"message": "Title and image_url are required."}, 400

        # Convert list of winners to CSV string if needed
        if isinstance(winners, list):
            winners = ", ".join(winners)

        try:
            badge = Badge(
                title=title,
                awarded=awarded,
                winners=winners,
                image_url=image_url
            )
            db.session.add(badge)
            db.session.commit()
            return serialize_badge(badge), 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to create badge", "error": str(e)}, 500


class BadgeResource(Resource):
    def get(self, badge_id):
        badge = Badge.query.get(badge_id)
        if not badge:
            return {"message": "Badge not found"}, 404
        return serialize_badge(badge), 200

    @jwt_required()
    def patch(self, badge_id):
        badge = Badge.query.get(badge_id)
        if not badge:
            return {"message": "Badge not found"}, 404

        data = request.get_json()
        badge.title = data.get("title", badge.title)
        badge.awarded = data.get("awarded", badge.awarded)

        winners = data.get("winners")
        if winners is not None:
            badge.winners = ", ".join(winners) if isinstance(winners, list) else winners

        badge.image_url = data.get("image_url", badge.image_url)

        try:
            db.session.commit()
            return serialize_badge(badge), 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to update badge", "error": str(e)}, 500

    @jwt_required()
    def delete(self, badge_id):
        badge = Badge.query.get(badge_id)
        if not badge:
            return {"message": "Badge not found"}, 404

        try:
            db.session.delete(badge)
            db.session.commit()
            return {"message": "Badge deleted successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to delete badge", "error": str(e)}, 500
