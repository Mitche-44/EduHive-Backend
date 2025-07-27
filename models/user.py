from extensions import db, bcrypt
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from sqlalchemy.orm import relationship
from extensions import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='learner')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)

    # Leaderboard fields
    points = db.Column(db.Integer, default=0)
    top_activity = db.Column(db.String(50))  # Cached most common activity (optional)

    # Relationships
    activities = relationship("LearnerActivity", back_populates="learner", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="learner", cascade="all, delete-orphan")

    serialize_rules = ('-password_hash',)

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        return f"<User {self.email}>"
    
    # def __repr__(self):
    #     return f"<User {self.username}>"
