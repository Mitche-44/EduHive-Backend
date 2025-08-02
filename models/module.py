from extensions import db
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
import enum

# Define status enum
class StatusEnum(enum.Enum):
    pending = 'pending'
    approved = 'approved'

class Module(db.Model, SerializerMixin):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)

    # Add this for card display
    image_url = db.Column(db.String(255))

    # Existing media_url
    media_url = db.Column(db.String(255))

    # Status
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.pending, nullable=False)

    # Foreign Key
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationships
    contributor = db.relationship("User", backref="modules")

    # Serialization rules
    serialize_rules = ('-contributor',)

    def __repr__(self):
        return f"<Module {self.title} by {self.contributor_id}>"
