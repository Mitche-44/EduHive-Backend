from extensions import db
from datetime import datetime

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    plan = db.Column(db.String(20), nullable=False)  # Free, Basic, Pro, Elite
    billing_cycle = db.Column(db.String(10), nullable=False)  # monthly or yearly
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.plan} - {self.billing_cycle}>"
