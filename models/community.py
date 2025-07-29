from extensions import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class CommunityPost(db.Model, SerializerMixin):
    __tablename__ = 'community_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    forum = db.Column(db.String(50), default="general")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    likes = db.Column(db.Integer, default=0)

    comments = db.relationship("Comment", backref="post", cascade="all, delete-orphan")

    serialize_rules = ('-author.password_hash', '-comments.post',)

class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    serialize_rules = ('-post.comments', '-author.password_hash',)
