from core.extensions import db
from datetime import datetime

class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey("path.id"), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    learner = db.relationship("User", back_populates="progress")
    path = db.relationship("Path", back_populates="progress_entries")
    
    __table_args__ = (
        db.UniqueConstraint('learner_id', 'path_id', name='unique_learner_progress'),
    )   