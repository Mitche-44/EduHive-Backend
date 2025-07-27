# models/path.py
from datetime import datetime
from sqlalchemy.orm import relationship
from extensions import db
from sqlalchemy_serializer import SerializerMixin

class Path(db.Model, SerializerMixin):
    __tablename__ = "paths"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    modules = relationship("Module", backref="path", cascade="all, delete-orphan")
    progress_entries = relationship("Progress", back_populates="path", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Path {self.title}>"
    
class Module(db.Model, SerializerMixin):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey("paths.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=1)
