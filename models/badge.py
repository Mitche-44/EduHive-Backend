from extensions import db
from sqlalchemy_serializer import SerializerMixin

class Badge(db.Model, SerializerMixin):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    awarded = db.Column(db.Integer, default=0)
    winners = db.Column(db.Text, nullable=True)  
    image_url = db.Column(db.String, nullable=False)

    def winner_list(self):
        """Returns the winners as a list from comma-separated string"""
        return [w.strip() for w in self.winners.split(',')] if self.winners else []

    serialize_rules = ()
