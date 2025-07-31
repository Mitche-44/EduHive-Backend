from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, socketio
from models.community import CommunityPost, Comment
from models import User

# GET all posts or filter by forum
class CommunityPostsResource(Resource):
    def options(self):
        return {}, 200

    def get(self):
        forum = request.args.get('forum', 'general')
        posts = CommunityPost.query.filter_by(forum=forum).order_by(CommunityPost.created_at.desc()).all()
        return [post.to_dict() for post in posts], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        forum = data.get('forum', 'general')
        user_id = get_jwt_identity()

        if not title or not content:
            return {"error": "Both title and content are required."}, 400

        post = CommunityPost(
            title=title,
            content=content,
            forum=forum,
            author_id=user_id
        )
        db.session.add(post)
        db.session.commit()

        # Emit real-time post to clients in that forum room
        socketio.emit('new_post', post.to_dict(), room=forum)

        return post.to_dict(), 200


class LikePostResource(Resource):
    def options(self, post_id):
        return {}, 200

    @jwt_required()
    def post(self, post_id):
        post = CommunityPost.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        post.likes += 1
        db.session.commit()

        # Emit like update
        socketio.emit('like_post', {'postId': post_id, 'likes': post.likes}, room=post.forum)

        return {"message": "Post liked", "likes": post.likes}, 200


class PostCommentResource(Resource):
    def options(self, post_id):
        return {}, 200

    @jwt_required()
    def post(self, post_id):
        data = request.get_json()
        content = data.get("content")
        user_id = get_jwt_identity()

        post = CommunityPost.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        if not content:
            return {"error": "Comment content is required"}, 400

        comment = Comment(
            post_id=post_id,
            author_id=user_id,
            content=content
        )
        db.session.add(comment)
        db.session.commit()

        # Emit new comment
        socketio.emit("new_comment", {
            "postId": post_id,
            "comment": comment.to_dict()
        }, room=post.forum)

        return comment.to_dict(), 200
