from extensions import db
from datetime import datetime
from .user import User 

class LeaderboardEntry(db.Model):
    __tablename__ = 'leaderboard_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    points = db.Column(db.Integer, default=0, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # e.g., "Courses", "Quizzes"
    joined_date = db.Column(db.Date, default=datetime.utcnow)

    avatar_url = db.Column(db.String(255))

    gold_medals = db.Column(db.Integer, default=0)
    silver_medals = db.Column(db.Integer, default=0)
    bronze_medals = db.Column(db.Integer, default=0)

    user = db.relationship('User', back_populates='leaderboard_entries')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.user.full_name,
            "joined": self.joined_date.strftime("%Y-%m"),
            "points": self.points,
            "avatar": self.avatar_url,
            "activity": self.activity_type,
            "medals": {
                "gold": self.gold_medals,
                "silver": self.silver_medals,
                "bronze": self.bronze_medals
            }
        }
