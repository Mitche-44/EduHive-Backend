# resources/path.py

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.path import Path
from models.user import User
from extensions import db

class PathListResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        """Learner: View approved paths"""
        paths = Path.query.filter_by(is_approved=True).all()
        return [p.to_dict() for p in paths], 200

    @jwt_required()
    def post(self):
        """Contributor: Submit new path"""
        user_id = get_jwt_identity()["id"]
        user = User.query.get_or_404(user_id)

        if user.role != "contributor":
            return {"error": "Only contributors can submit paths"}, 403

        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        category = data.get("category")
        thumbnail = data.get("thumbnail")
        content_link = data.get("content_link")

        if not all([title, description, category]):
            return {"error": "Missing required fields"}, 400

        path = Path(
            title=title,
            description=description,
            category=category,
            thumbnail=thumbnail,
            content_link=content_link,
            contributor_id=user.id
        )

        db.session.add(path)
        db.session.commit()
        return path.to_dict(), 201

class ContributorPathListResource(Resource):
    @jwt_required()
    def get(self):
        """Contributor: View their own submitted paths"""
        user_id = get_jwt_identity()["id"]
        paths = Path.query.filter_by(contributor_id=user_id).all()
        return [p.to_dict() for p in paths], 200

class PendingPathListResource(Resource):
    @jwt_required()
    def get(self):
        """Admin: View all pending paths"""
        user = User.query.get(get_jwt_identity()["id"])
        if user.role != "admin":
            return {"error": "Admins only"}, 403

        pending = Path.query.filter_by(is_approved=False).all()
        return [p.to_dict() for p in pending], 200

class PathApprovalResource(Resource):
    @jwt_required()
    def patch(self, id):
        """Admin: Approve a path"""
        user = User.query.get(get_jwt_identity()["id"])
        if user.role != "admin":
            return {"error": "Admins only"}, 403

        path = Path.query.get_or_404(id)
        path.is_approved = True
        db.session.commit()
        return path.to_dict(), 200
class PathUpdateResource(Resource):
    @jwt_required()
    def patch(self, id):
        """Contributor: Edit own path before approval"""
        user_id = get_jwt_identity()["id"]
        user = User.query.get_or_404(user_id)

        path = Path.query.get_or_404(id)

        if user.role != "contributor":
            return {"error": "Only contributors can edit paths"}, 403

        if path.contributor_id != user.id:
            return {"error": "You can only edit your own paths"}, 403

        if path.is_approved:
            return {"error": "Cannot edit approved path"}, 403

        data = request.get_json()

        path.title = data.get("title", path.title)
        path.description = data.get("description", path.description)
        path.category = data.get("category", path.category)
        path.thumbnail = data.get("thumbnail", path.thumbnail)
        path.content_link = data.get("content_link", path.content_link)

        db.session.commit()
        return path.to_dict(), 200
