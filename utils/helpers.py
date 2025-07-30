# Add these functions to your existing utils/helpers.py file

from flask import request
from datetime import datetime, timedelta
import secrets
import string

def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_user_agent():
    """Get user agent from request"""
    return request.headers.get('User-Agent', 'Unknown')

def generate_quiz_id(unit, subject):
    """Generate a unique quiz ID based on unit and subject"""
    # Clean subject name
    clean_subject = ''.join(c for c in subject if c.isalnum() or c in '-_')
    clean_subject = clean_subject[:20]  # Limit length

    # Generate random suffix
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))

    return f"{unit}-{clean_subject}-{random_suffix}".lower()

def calculate_grade_from_score(score):
    """Calculate letter grade from percentage score"""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if not seconds:
        return "0 seconds"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ', '.join(parts)

def calculate_quiz_statistics(attempts):
    """Calculate comprehensive statistics for quiz attempts"""
    if not attempts:
        return {
            'total_attempts': 0,
            'unique_users': 0,
            'average_score': 0,
            'median_score': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'pass_rate': 0,
            'grade_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0},
            'average_time': 0
        }

    scores = [a.score for a in attempts]
    times = [a.time_taken for a in attempts if a.time_taken]
    passed_attempts = [a for a in attempts if a.is_passed]

    # Calculate grade distribution
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for score in scores:
        grade = calculate_grade_from_score(score)
        grade_distribution[grade] += 1

    # Calculate median score
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    if n % 2 == 0:
        median_score = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
    else:
        median_score = sorted_scores[n//2]

    return {
        'total_attempts': len(attempts),
        'unique_users': len(set(a.user_id for a in attempts)),
        'average_score': round(sum(scores) / len(scores), 2),
        'median_score': round(median_score, 2),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'pass_rate': round((len(passed_attempts) / len(attempts)) * 100, 2),
        'grade_distribution': grade_distribution,
        'average_time': round(sum(times) / len(times), 0) if times else 0
    }

def get_quiz_difficulty_color(difficulty):
    """Get color code for quiz difficulty"""
    colors = {
        'easy': '#4CAF50',    # Green
        'medium': '#FF9800',  # Orange
        'hard': '#F44336'     # Red
    }
    return colors.get(difficulty.lower(), '#757575')  # Default gray

def get_status_color(status):
    """Get color code for quiz status"""
    colors = {
        'active': '#4CAF50',      # Green
        'pending': '#2196F3',     # Blue
        'completed': '#4CAF50',   # Green
        'submitted': '#4CAF50',   # Green
        'expired': '#757575',     # Gray
        'inactive': '#757575'     # Gray
    }
    return colors.get(status.lower(), '#757575')

def format_quiz_deadline(deadline):
    """Format quiz deadline with relative time"""
    now = datetime.utcnow()

    if deadline < now:
        time_diff = now - deadline
        if time_diff.days > 0:
            return f"Expired {time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"Expired {hours} hour{'s' if hours != 1 else ''} ago"
        else:
            minutes = time_diff.seconds // 60
            return f"Expired {minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        time_diff = deadline - now
        if time_diff.days > 0:
            return f"Due in {time_diff.days} day{'s' if time_diff.days != 1 else ''}"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"Due in {hours} hour{'s' if hours != 1 else ''}"
        else:
            minutes = time_diff.seconds // 60
            return f"Due in {minutes} minute{'s' if minutes != 1 else ''}"

def calculate_xp_for_quiz(quiz, score, is_passed):
    """Calculate XP earned for quiz completion"""
    base_xp = quiz.total_questions * 5  # 5 XP per question

    if not is_passed:
        return base_xp // 2  # Half XP for failed attempts

    # Bonus XP based on score
    if score >= 95:
        bonus_multiplier = 2.0  # Perfect score bonus
    elif score >= 90:
        bonus_multiplier = 1.5  # Excellent bonus
    elif score >= 80:
        bonus_multiplier = 1.2  # Good bonus
    else:
        bonus_multiplier = 1.0  # Standard XP

    # Difficulty multiplier
    difficulty_multipliers = {
        'easy': 1.0,
        'medium': 1.2,
        'hard': 1.5
    }

    # Calculate average difficulty of questions
    difficulties = [q.difficulty for q in quiz.questions if q.difficulty]
    if difficulties:
        avg_difficulty = 'medium'  # Default
        difficulty_counts = {'easy': 0, 'medium': 0, 'hard': 0}
        for diff in difficulties:
            difficulty_counts[diff] += 1

        # Get most common difficulty
        avg_difficulty = max(difficulty_counts, key=difficulty_counts.get)
        difficulty_multiplier = difficulty_multipliers[avg_difficulty]
    else:
        difficulty_multiplier = 1.0

    total_xp = int(base_xp * bonus_multiplier * difficulty_multiplier)
    return total_xp

def generate_quiz_summary_data(quiz, user_id=None):
    """Generate comprehensive quiz summary data"""
    from models.quiz_attempt import QuizAttempt

    # Get all attempts for this quiz
    all_attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id, status='completed').all()

    # Calculate general statistics
    stats = calculate_quiz_statistics(all_attempts)

    summary = {
        'quiz_info': {
            'id': quiz.id,
            'subject': quiz.subject,
            'unit': quiz.unit,
            'description': quiz.description,
            'total_questions': quiz.total_questions,
            'passing_score': quiz.passing_score,
            'time_limit': quiz.time_limit,
            'max_attempts': quiz.max_attempts,
            'deadline': quiz.deadline.isoformat() if quiz.deadline else None,
            'deadline_formatted': format_quiz_deadline(quiz.deadline) if quiz.deadline else None,
            'status': quiz.status,
            'is_active': quiz.is_active
        },
        'statistics': stats,
        'performance_metrics': {
            'difficulty_rating': 'Easy' if stats['pass_rate'] > 80 else 'Hard' if stats['pass_rate'] < 50 else 'Medium',
            'engagement_level': 'High' if stats['total_attempts'] > 50 else 'Medium' if stats['total_attempts'] > 10 else 'Low'
        }
    }

    # Add user-specific data if user_id provided
    if user_id:
        user_attempts = quiz.get_user_attempts(user_id)
        user_best_score = quiz.get_user_best_score(user_id)
        can_attempt, message = quiz.can_user_attempt(user_id)

        summary['user_data'] = {
            'attempts_count': len(user_attempts),
            'best_score': user_best_score,
            'best_grade': calculate_grade_from_score(user_best_score) if user_best_score else None,
            'can_attempt': can_attempt,
            'attempt_message': message,
            'is_completed': user_best_score is not None and user_best_score >= quiz.passing_score,
            'recent_attempts': [a.get_attempt_summary() for a in user_attempts[-3:]]  # Last 3 attempts
        }

    return summary

def validate_quiz_time_window(quiz, current_time=None):
    """Validate if quiz is within the allowed time window"""
    if current_time is None:
        current_time = datetime.utcnow()

    if current_time < quiz.issue_date:
        return False, f"Quiz starts on {quiz.issue_date.strftime('%Y-%m-%d %H:%M')}"

    if current_time > quiz.deadline:
        return False, f"Quiz deadline passed on {quiz.deadline.strftime('%Y-%m-%d %H:%M')}"

    return True, "Quiz is available"

def shuffle_quiz_questions(questions, seed=None):
    """Shuffle quiz questions and options for randomization"""
    import random

    if seed:
        random.seed(seed)

    shuffled_questions = questions.copy()
    random.shuffle(shuffled_questions)

    # Shuffle options for multiple choice questions
    for question in shuffled_questions:
        if question.question_type == 'multiple_choice' and question.options:
            options_with_indices = list(enumerate(question.options))
            random.shuffle(options_with_indices)

            # Update the question data
            question.shuffled_options = [opt for idx, opt in options_with_indices]
            question.shuffled_correct_answer = next(
                new_idx for new_idx, (old_idx, _) in enumerate(options_with_indices)
                if old_idx == question.correct_answer
            )

    return shuffled_questions
# utils/helpers.py
# Utility functions for the EduHive application (email management, user creation)
def get_or_create_user(email, **kwargs):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(email=email, **kwargs)
    db.session.add(user)
    db.session.commit()
    return user
