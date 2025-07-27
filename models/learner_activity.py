from core.extensions import db
from datetime import datetime

class LearnerActivity(db.Model):
    __tablename__ = "learner_activities"

    id = db.Column(db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., "Quiz", "Module", "Path"
    ref_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    learner = db.relationship("User", back_populates="activities")
