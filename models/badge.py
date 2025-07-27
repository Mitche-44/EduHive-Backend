from extensions import db
from sqlalchemy_serializer import SerializerMixin

class Badge(db.Model, SerializerMixin):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    awarded = db.Column(db.Integer, default=0)
    winners = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String, nullable=False)

    # Exclude winners and use winner_list in the API instead
    serialize_rules = ('-winners',)

    @property
    def winner_list(self):
        """Returns winners as a list from the comma-separated string."""
        return [winner.strip() for winner in self.winners.split(',')] if self.winners else []

    def __repr__(self):
        return f"<Badge {self.title}>"
