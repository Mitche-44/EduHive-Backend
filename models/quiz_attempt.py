from extensions import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

class QuizAttempt(db.Model, SerializerMixin):
    __tablename__ = 'quiz_attempts'

    serialize_rules = ('-user.quiz_attempts', '-quiz.quiz_attempts', '-question_attempts.quiz_attempt')

    id = db.Column(db.Integer, primary_key=True)
    attempt_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, submitted
    score = db.Column(db.Float, default=0.0)  # Percentage score
    total_points = db.Column(db.Integer, default=0)
    max_points = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    time_started = db.Column(db.DateTime, default=datetime.utcnow)
    time_completed = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # Total time in seconds
    ip_address = db.Column(db.String(45))  # For tracking/security
    user_agent = db.Column(db.String(500))  # Browser info

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.String(50), db.ForeignKey('quizzes.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='quiz_attempts')
    question_attempts = db.relationship('QuestionAttempt', backref='quiz_attempt', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<QuizAttempt {self.id}: User {self.user_id} - Quiz {self.quiz_id}>'

    def calculate_score(self):
        """Calculate and update the score based on question attempts"""
        if not self.question_attempts:
            return 0.0

        total_points = sum(qa.points_earned for qa in self.question_attempts)
        max_points = sum(qa.question.points for qa in self.question_attempts)
        correct_count = sum(1 for qa in self.question_attempts if qa.is_correct)

        self.total_points = total_points
        self.max_points = max_points
        self.correct_answers = correct_count
        self.total_questions = len(self.question_attempts)

        # Calculate percentage score
        if max_points > 0:
            self.score = (total_points / max_points) * 100
        else:
            self.score = 0.0

        return self.score

    def submit_attempt(self):
        """Mark the attempt as completed and calculate final score"""
        self.status = 'completed'
        self.time_completed = datetime.utcnow()

        if self.time_started:
            time_diff = self.time_completed - self.time_started
            self.time_taken = int(time_diff.total_seconds())

        self.calculate_score()
        db.session.commit()

        return self.score

    @property
    def is_passed(self):
        """Check if the attempt passed based on quiz passing score"""
        if self.quiz and self.status == 'completed':
            return self.score >= self.quiz.passing_score
        return False

    @property
    def grade(self):
        """Get letter grade based on score"""
        if self.score >= 90:
            return 'A'
        elif self.score >= 80:
            return 'B'
        elif self.score >= 70:
            return 'C'
        elif self.score >= 60:
            return 'D'
        else:
            return 'F'

    def get_attempt_summary(self):
        """Get a summary of the quiz attempt"""
        return {
            'id': self.id,
            'attempt_number': self.attempt_number,
            'status': self.status,
            'score': self.score,
            'grade': self.grade,
            'is_passed': self.is_passed,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'time_started': self.time_started.isoformat() if self.time_started else None,
            'time_completed': self.time_completed.isoformat() if self.time_completed else None,
            'quiz': {
                'id': self.quiz.id,
                'subject': self.quiz.subject,
                'unit': self.quiz.unit,
                'passing_score': self.quiz.passing_score
            } if self.quiz else None
        }