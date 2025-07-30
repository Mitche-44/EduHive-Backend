from extensions import db, bcrypt
from sqlalchemy_serializer import SerializerMixin




class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    google_id = db.Column(db.String, unique=True) 
    role = db.Column(db.String(20), default='learner')
    is_approved = db.Column(db.Boolean, default=False)

    # Relationship to leaderboard
    leaderboard_entries = db.relationship("LeaderboardEntry", back_populates="user", cascade="all, delete-orphan", lazy=True)

    subscriptions = db.relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

    
    serialize_rules = ('-password_hash',)

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.email}>"
