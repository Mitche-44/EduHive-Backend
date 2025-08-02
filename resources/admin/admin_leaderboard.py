from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.leaderboard import LeaderboardEntry
from models.user import User
from extensions import db

admin_leaderboard_bp = Blueprint("admin_leaderboard", __name__, url_prefix="/api/admin/leaderboard")

@admin_leaderboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_admin_leaderboard():
    entries = (
        db.session.query(LeaderboardEntry)
        .join(User)
        .order_by(LeaderboardEntry.total_xp.desc())
        .limit(50)
        .all()
    )

    leaderboard_data = [
        {
            "user_id": entry.user.id,
            "name": f"{entry.user.first_name} {entry.user.last_name}",
            "points": entry.total_xp,
            "badge": entry.badges_earned or None,
        }
        for entry in entries
    ]

    return jsonify(leaderboard_data), 200
