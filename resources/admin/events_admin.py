from flask_socketio import emit
from models.leaderboard import LeaderboardEntry
from models.user import User
from extensions import socketio, db

@socketio.on('connect', namespace='/admin')
def handle_admin_connect():
    print("Admin connected to leaderboard socket")

def emit_leaderboard_update():
    entries = (
        db.session.query(LeaderboardEntry)
        .join(User)
        .order_by(LeaderboardEntry.total_xp.desc())
        .limit(10)
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

    socketio.emit("leaderboard_update", leaderboard_data, namespace="/admin")
