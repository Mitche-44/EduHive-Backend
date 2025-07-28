from extensions import db
from datetime import datetime
import uuid

class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
