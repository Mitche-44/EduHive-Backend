from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models explicitly
from .user import User
from .learner_activity import LearnerActivity
from .progress import Progress
from .path import Path
# from .module import Module
# from .quiz import Quiz
# from .quiz_attempt import QuizAttempt
# from .subscription import Subscription
# from .badge import Badge
# from .chat_message import ChatMessage
# from .comment import Comment
# from .community_post import CommunityPost
# from .approval_request import ApprovalRequest