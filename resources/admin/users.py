from flask_restful import Resource
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from models.user import User
from extensions import db

class ApproveUser(Resource):
    @jwt_required()
    @role_required("admin")
    def patch(self, user_id):
        user = User.query.get_or_404(user_id)
        user.is_approved = True
        db.session.commit()
        return {"msg": f"User {user.email} approved successfully"}
