from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.module import Module, StatusEnum
from models.user import User

# -------- Validation ----------
def validate_module_data(data, is_update=False):
    errors = {}

    if not is_update or "title" in data:
        if not data.get("title"):
            errors["title"] = "Title is required."
        elif len(data["title"]) < 3:
            errors["title"] = "Title must be at least 3 characters long."

    if not is_update or "description" in data:
        if not data.get("description"):
            errors["description"] = "Description is required."

    if "status" in data:
        try:
            StatusEnum(data["status"])  # Check if valid Enum
        except ValueError:
            errors["status"] = "Invalid status. Must be 'pending' or 'approved'."

    return errors
# --------------------------------


class ContributorModuleListResource(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user_id = identity["id"]
        modules = Module.query.filter_by(contributor_id=user_id).all()
        return [m.to_dict() for m in modules], 200

    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        user_id = identity["id"]
        data = request.get_json()

        errors = validate_module_data(data)
        if errors:
            return {"errors": errors}, 400

        try:
            module = Module(
                title=data["title"],
                description=data["description"],
                content=data.get("content"),
                media_url=data.get("media_url"),
                status=StatusEnum(data.get("status", "pending")),
                contributor_id=user_id
            )

            db.session.add(module)
            db.session.commit()

            return module.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            return {"message": "Error creating module", "error": str(e)}, 500


class ContributorModuleResource(Resource):
    @jwt_required()
    def get(self, module_id):
        identity = get_jwt_identity()
        user_id = identity["id"]
        module = Module.query.get_or_404(module_id)

        if module.contributor_id != user_id:
            return {"message": "Forbidden: Not your module."}, 403

        return module.to_dict(), 200

    @jwt_required()
    def patch(self, module_id):
        identity = get_jwt_identity()
        user_id = identity["id"]
        module = Module.query.get_or_404(module_id)

        if module.contributor_id != user_id:
            return {"message": "Forbidden: Not your module."}, 403

        data = request.get_json()
        errors = validate_module_data(data, is_update=True)
        if errors:
            return {"errors": errors}, 400

        if "title" in data:
            module.title = data["title"]
        if "description" in data:
            module.description = data["description"]
        if "content" in data:
            module.content = data["content"]
        if "media_url" in data:
            module.media_url = data["media_url"]
        if "status" in data:
            module.status = StatusEnum(data["status"])

        try:
            db.session.commit()
            return module.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Update failed", "error": str(e)}, 500

    @jwt_required()
    def delete(self, module_id):
        identity = get_jwt_identity()
        user_id = identity["id"]
        module = Module.query.get_or_404(module_id)

        if module.contributor_id != user_id:
            return {"message": "Forbidden: Not your module."}, 403

        try:
            db.session.delete(module)
            db.session.commit()
            return {"message": "Module deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Delete failed", "error": str(e)}, 500
