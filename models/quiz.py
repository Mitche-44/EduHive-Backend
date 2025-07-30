from extensions import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class Quiz(db.Model, SerializerMixin):
    __tablename__ = 'quizzes'

    serialize_rules = ('-quiz_attempts.quiz', '-module.quizzes', '-questions.quiz')

    id = db.Column(db.String(50), primary_key=True)
    unit = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    total_questions = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Integer, default=70)  # Percentage
    time_limit = db.Column(db.Integer)  # Minutes
    max_attempts = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    module = db.relationship('Module', backref='quizzes')
    creator = db.relationship('User', backref='created_quizzes')
    questions = db.relationship('QuizQuestion', backref='quiz', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='quiz', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Quiz {self.id}: {self.subject}>'

    @property
    def status(self):
        """Calculate quiz status based on current date and deadline"""
        now = datetime.utcnow()
        if now > self.deadline:
            return 'Expired'
        elif now < self.issue_date:
            return 'Not Started'
        else:
            return 'Active'

    def get_user_attempts(self, user_id):
        """Get all attempts by a specific user"""
        from models.quiz_attempt import QuizAttempt
        return QuizAttempt.query.filter_by(quiz_id=self.id, user_id=user_id).all()

    def get_user_best_score(self, user_id):
        """Get user's best score for this quiz"""
        attempts = self.get_user_attempts(user_id)
        if not attempts:
            return None
        return max(attempt.score for attempt in attempts)

    def can_user_attempt(self, user_id):
        """Check if user can attempt this quiz"""
        if not self.is_active or self.status != 'Active':
            return False, "Quiz is not available"

        attempts = self.get_user_attempts(user_id)
        if len(attempts) >= self.max_attempts:
            return False, f"Maximum attempts ({self.max_attempts}) exceeded"

        return True, "Can attempt"


class QuizQuestion(db.Model, SerializerMixin):
    __tablename__ = 'quiz_questions'

    serialize_rules = ('-quiz.questions', '-quiz_attempts.question')

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='multiple_choice')  # multiple_choice, true_false, short_answer
    options = db.Column(db.JSON)  # Store options as JSON array
    correct_answer = db.Column(db.Integer)  # Index of correct option for multiple choice
    correct_answer_text = db.Column(db.Text)  # For short answer questions
    explanation = db.Column(db.Text)  # Optional explanation for the answer
    points = db.Column(db.Integer, default=1)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=False)

    # Relationships
    question_attempts = db.relationship('QuestionAttempt', backref='question', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<QuizQuestion {self.id}: {self.question_text[:50]}...>'

    def is_correct_answer(self, user_answer):
        """Check if the user's answer is correct"""
        if self.question_type == 'multiple_choice':
            return int(user_answer) == self.correct_answer
        elif self.question_type == 'true_false':
            return int(user_answer) == self.correct_answer
        elif self.question_type == 'short_answer':
            # Simple case-insensitive comparison for short answers
            return str(user_answer).lower().strip() == self.correct_answer_text.lower().strip()
        return False


class QuestionAttempt(db.Model, SerializerMixin):
    __tablename__ = 'question_attempts'

    serialize_rules = ('-quiz_attempt.question_attempts', '-question.question_attempts')

    id = db.Column(db.Integer, primary_key=True)
    user_answer = db.Column(db.Text)  # User's selected answer
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer)  # Seconds spent on this question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)

    def __repr__(self):
        return f'<QuestionAttempt {self.id}: Q{self.question_id} - {"Correct" if self.is_correct else "Incorrect"}>'