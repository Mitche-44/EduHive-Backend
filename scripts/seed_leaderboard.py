
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models.user import User
from models.leaderboard import LeaderboardEntry
from datetime import datetime

app = create_app()

with app.app_context():
    # Drop and recreate tables (optional, be cautious in production)
    # db.drop_all()
    # db.create_all()

    # Create dummy users
    user1 = User(
        first_name="Alicee",
        last_name="Johnson",
        email="alicejohn@example.com",
        role="learner",
        is_approved=True
    )
    user1.password = "password1234"

    user2 = User(
        first_name="Bob",
        last_name="Smith",
        email="boby@example.com",
        role="learner",
        is_approved=True
    )
    user2.password = "password123"

    db.session.add_all([user1, user2])
    db.session.commit()

    # Create leaderboard entries
    entry1 = LeaderboardEntry(
        user_id=user1.id,
        points=1500,
        activity_type="Courses",
        joined_date=datetime(2024, 5, 1),
        avatar_url="https://api.dicebear.com/6.x/thumbs/svg?seed=Alice",
        gold_medals=3,
        silver_medals=2,
        bronze_medals=1
    )

    entry2 = LeaderboardEntry(
        user_id=user2.id,
        points=1200,
        activity_type="Quizzes",
        joined_date=datetime(2024, 6, 15),
        avatar_url="https://api.dicebear.com/6.x/thumbs/svg?seed=Bob",
        gold_medals=1,
        silver_medals=3,
        bronze_medals=2
    )

    db.session.add_all([entry1, entry2])
    db.session.commit()

    print("✅ Seeded leaderboard data successfully.")
