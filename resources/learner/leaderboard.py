from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.leaderboard import LeaderboardEntry
from models.user import User
from extensions import db

leaderboard_bp = Blueprint("leaderboard", __name__)

@leaderboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_leaderboard():
    # Fetch leaderboard entries ordered by XP descending
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
            "total_xp": entry.total_xp,
            "badges": entry.badges_earned
        }
        for entry in entries
    ]

    return jsonify({"leaderboard": leaderboard_data}), 200
