from app import create_app
from extensions import db
from models.user import User  # Adjust the path if needed

def seed_users():
    users = [
        User(
            first_name="Alice",
            last_name="Admin",
            email="admin@example.com",
            role="admin",
            is_approved=True
        ),
        User(
            first_name="Bob",
            last_name="Contributor",
            email="contributor@example.com",
            role="contributor",
            is_approved=True
        ),
        User(
            first_name="Charlie",
            last_name="Learner",
            email="learner@example.com",
            
            role="learner",
            is_approved=True
        )
    ]

    # Set passwords using the setter
    users[0].password = "admin123"
    users[1].password = "contrib123"
    users[2].password = "learner123"

    db.session.bulk_save_objects(users)
    db.session.commit()

    print("✅ Seeded users with roles: admin, contributor, learner.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Drop and recreate tables for fresh seeding — only use in dev
        db.drop_all()
        db.create_all()

        seed_users()
