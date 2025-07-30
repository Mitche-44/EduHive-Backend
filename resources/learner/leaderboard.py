from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.leaderboard import LeaderboardEntry
from models.user import User
from extensions import db
from extensions import socketio
from datetime import datetime

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api/leaderboard")

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

@leaderboard_bp.route("/update_xp", methods=["POST"])
@jwt_required()
def update_xp():
    data = request.get_json()
    user_id = get_jwt_identity()
    xp_gain = data.get("xp", 0)

    if not isinstance(xp_gain, int) or xp_gain <= 0:
        return jsonify({"error": "Invalid XP value"}), 400

    entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()

    if not entry:
        entry = LeaderboardEntry(user_id=user_id, total_xp=0, badges_earned=[])
        db.session.add(entry)

    entry.total_xp += xp_gain
    assign_badges(entry)
    db.session.commit()

    socketio.emit("leaderboard_updated", {
        "user_id": user_id,
        "total_xp": entry.total_xp,
        "badges": entry.badges_earned
    }, namespace="/leaderboard")

    return jsonify({"success": True, "total_xp": entry.total_xp}), 200


def assign_badges(entry):
    badges = set(entry.badges_earned or [])

    if entry.total_xp >= 1000:
        badges.add("Top Scorer")
    elif entry.total_xp >= 500:
        badges.add("Rising Star")

    entry.badges_earned = list(badges)
