# Combined validation functions for quiz/learning management application

from datetime import datetime
import re

# ============================================================================
# QUIZ VALIDATION FUNCTIONS (from paste.txt - unchanged)
# ============================================================================

def validate_quiz_data(data):
    """Validate quiz creation/update data"""
    errors = []

    # Required fields
    required_fields = ['id', 'unit', 'subject', 'deadline']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')

    # Validate quiz ID format
    if 'id' in data:
        quiz_id = data['id']
        if not re.match(r'^[a-zA-Z0-9\-_]+$', quiz_id):
            errors.append('Quiz ID can only contain letters, numbers, hyphens, and underscores')
        if len(quiz_id) > 50:
            errors.append('Quiz ID must be 50 characters or less')

    # Validate unit format
    if 'unit' in data:
        unit = data['unit']
        if not re.match(r'^[0-9]{2}(-[0-9]+)?$', unit):
            errors.append('Unit must be in format "01" or "01-2"')

    # Validate subject length
    if 'subject' in data and len(data['subject']) > 200:
        errors.append('Subject must be 200 characters or less')

    # Validate description length
    if 'description' in data and data['description'] and len(data['description']) > 1000:
        errors.append('Description must be 1000 characters or less')

    # Validate deadline format and date
    if 'deadline' in data:
        try:
            deadline_str = data['deadline']
            # Try different date formats
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')

            # Check if deadline is in the future
            if deadline <= datetime.utcnow():
                errors.append('Deadline must be in the future')

        except ValueError:
            errors.append('Invalid deadline format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS')

    # Validate issue_date if provided
    if 'issue_date' in data and data['issue_date']:
        try:
            issue_date_str = data['issue_date']
            try:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
        except ValueError:
            errors.append('Invalid issue date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS')

    # Validate passing_score
    if 'passing_score' in data:
        try:
            passing_score = int(data['passing_score'])
            if not 0 <= passing_score <= 100:
                errors.append('Passing score must be between 0 and 100')
        except (ValueError, TypeError):
            errors.append('Passing score must be a valid integer')

    # Validate time_limit
    if 'time_limit' in data and data['time_limit'] is not None:
        try:
            time_limit = int(data['time_limit'])
            if time_limit <= 0:
                errors.append('Time limit must be a positive integer (minutes)')
        except (ValueError, TypeError):
            errors.append('Time limit must be a valid integer')

    # Validate max_attempts
    if 'max_attempts' in data:
        try:
            max_attempts = int(data['max_attempts'])
            if not 1 <= max_attempts <= 10:
                errors.append('Max attempts must be between 1 and 10')
        except (ValueError, TypeError):
            errors.append('Max attempts must be a valid integer')

    return errors


def validate_question_data(data):
    """Validate quiz question data"""
    errors = []

    # Required fields
    if 'question_text' not in data or not data['question_text']:
        errors.append('Question text is required')

    # Validate question text length
    if 'question_text' in data and len(data['question_text']) > 1000:
        errors.append('Question text must be 1000 characters or less')

    # Validate question type
    valid_types = ['multiple_choice', 'true_false', 'short_answer']
    question_type = data.get('question_type', 'multiple_choice')
    if question_type not in valid_types:
        errors.append(f'Question type must be one of: {", ".join(valid_types)}')

    # Validate based on question type
    if question_type == 'multiple_choice':
        # Validate options
        if 'options' not in data or not isinstance(data['options'], list):
            errors.append('Options must be provided as a list for multiple choice questions')
        elif len(data['options']) < 2:
            errors.append('Multiple choice questions must have at least 2 options')
        elif len(data['options']) > 6:
            errors.append('Multiple choice questions can have at most 6 options')
        else:
            # Check if all options are non-empty strings
            for i, option in enumerate(data['options']):
                if not isinstance(option, str) or not option.strip():
                    errors.append(f'Option {i+1} must be a non-empty string')

        # Validate correct answer
        if 'correct_answer' not in data:
            errors.append('Correct answer index is required for multiple choice questions')
        else:
            try:
                correct_answer = int(data['correct_answer'])
                if 'options' in data and isinstance(data['options'], list):
                    if not 0 <= correct_answer < len(data['options']):
                        errors.append('Correct answer index is out of range')
            except (ValueError, TypeError):
                errors.append('Correct answer must be a valid integer index')

    elif question_type == 'true_false':
        # Validate correct answer for true/false
        if 'correct_answer' not in data:
            errors.append('Correct answer is required for true/false questions')
        else:
            try:
                correct_answer = int(data['correct_answer'])
                if correct_answer not in [0, 1]:
                    errors.append('Correct answer for true/false must be 0 (False) or 1 (True)')
            except (ValueError, TypeError):
                errors.append('Correct answer must be 0 or 1 for true/false questions')

    elif question_type == 'short_answer':
        # Validate correct answer text
        if 'correct_answer_text' not in data or not data['correct_answer_text']:
            errors.append('Correct answer text is required for short answer questions')
        elif len(data['correct_answer_text']) > 500:
            errors.append('Correct answer text must be 500 characters or less')

    # Validate explanation length
    if 'explanation' in data and data['explanation'] and len(data['explanation']) > 1000:
        errors.append('Explanation must be 1000 characters or less')

    # Validate points
    if 'points' in data:
        try:
            points = int(data['points'])
            if not 1 <= points <= 10:
                errors.append('Points must be between 1 and 10')
        except (ValueError, TypeError):
            errors.append('Points must be a valid integer')

    # Validate difficulty
    valid_difficulties = ['easy', 'medium', 'hard']
    if 'difficulty' in data and data['difficulty'] not in valid_difficulties:
        errors.append(f'Difficulty must be one of: {", ".join(valid_difficulties)}')

    # Validate order_index
    if 'order_index' in data:
        try:
            order_index = int(data['order_index'])
            if order_index < 0:
                errors.append('Order index must be a non-negative integer')
        except (ValueError, TypeError):
            errors.append('Order index must be a valid integer')

    return errors


def validate_quiz_submission(data):
    """Validate quiz submission data"""
    errors = []

    # Check if answers are provided
    if 'answers' not in data:
        errors.append('Answers are required')
        return errors

    answers = data['answers']
    if not isinstance(answers, dict):
        errors.append('Answers must be provided as a dictionary')
        return errors

    # Validate each answer
    for question_id, answer in answers.items():
        # Validate question ID
        try:
            int(question_id)
        except (ValueError, TypeError):
            errors.append(f'Invalid question ID: {question_id}')
            continue

        # Validate answer is not empty
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            errors.append(f'Answer for question {question_id} cannot be empty')

    return errors


def validate_quiz_id_format(quiz_id):
    """Validate quiz ID format"""
    if not quiz_id:
        return False, "Quiz ID is required"

    if not isinstance(quiz_id, str):
        return False, "Quiz ID must be a string"

    if len(quiz_id) > 50:
        return False, "Quiz ID must be 50 characters or less"

    if not re.match(r'^[a-zA-Z0-9\-_]+$', quiz_id):
        return False, "Quiz ID can only contain letters, numbers, hyphens, and underscores"

    return True, "Valid quiz ID"


def validate_unit_format(unit):
    """Validate unit format"""
    if not unit:
        return False, "Unit is required"

    if not isinstance(unit, str):
        return False, "Unit must be a string"

    if not re.match(r'^[0-9]{2}(-[0-9]+)?$', unit):
        return False, 'Unit must be in format "01" or "01-2"'

    return True, "Valid unit format"


def validate_date_range(start_date, end_date):
    """Validate date range"""
    if start_date >= end_date:
        return False, "Start date must be before end date"

    if end_date <= datetime.utcnow():
        return False, "End date must be in the future"

    return True, "Valid date range"


def validate_quiz_attempt_data(data, quiz):
    """Validate quiz attempt submission"""
    errors = []

    if not quiz:
        errors.append("Quiz not found")
        return errors

    if not quiz.is_active:
        errors.append("Quiz is not active")

    if quiz.status != 'Active':
        errors.append(f"Quiz is not available (status: {quiz.status})")

    # Validate answers match quiz questions
    if 'answers' in data:
        question_ids = {str(q.id) for q in quiz.questions}
        answer_ids = set(data['answers'].keys())

        # Check for extra answers
        extra_answers = answer_ids - question_ids
        if extra_answers:
            errors.append(f"Invalid question IDs: {', '.join(extra_answers)}")

        # Check for missing answers (optional - some quizzes might allow partial submission)
        missing_answers = question_ids - answer_ids
        if missing_answers and len(missing_answers) == len(question_ids):
            errors.append("At least one answer must be provided")

    return errors

# ============================================================================
# ADDITIONAL VALIDATION FUNCTIONS (from user's code - unchanged)
# ============================================================================

def is_valid_url(url):
    url_regex = re.compile(
        r'^(https?://)?'                   # Optional scheme
        r'([a-zA-Z0-9.-]+)'                # Domain
        r'(\.[a-zA-Z]{2,6})'               # TLD
        r'(/[a-zA-Z0-9&%_.\-/]*)?$'        # Path
    )
    return re.match(url_regex, url)

def validate_module_data(data):
    errors = {}

    # Title
    if not data.get("title") or len(data["title"].strip()) < 3:
        errors["title"] = "Title is required and must be at least 3 characters long."

    # Description
    if not data.get("description") or len(data["description"].strip()) < 10:
        errors["description"] = "Description is required and must be at least 10 characters long."

    # Content
    if "content" in data and not isinstance(data["content"], str):
        errors["content"] = "Content must be a string."

    # Media URL
    if data.get("media_url") and not is_valid_url(data["media_url"]):
        errors["media_url"] = "Media URL must be a valid URL."

    # Status
    if data.get("status") and data["status"] not in ["pending", "approved"]:
        errors["status"] = "Status must be either 'pending' or 'approved'."

    # Contributor ID
    if "contributor_id" not in data:
        errors["contributor_id"] = "Contributor ID is required."

    return errors


def validate_signup_data(data):
    errors = {}

    if "first_name" not in data or not data["first_name"].isalpha():
        errors["first_name"] = "First name must be alphabetic."
    if "last_name" not in data or not data["last_name"].isalpha():
        errors["last_name"] = "Last name must be alphabetic."
    if "email" not in data or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        errors["email"] = "Invalid email format."
    if "password" not in data or len(data["password"]) < 6:
        errors["password"] = "Password must be at least 6 characters."

    return errors


def validate_login_data(data):
    errors = {}
    if "email" not in data:
        errors["email"] = "Email is required."
    if "password" not in data:
        errors["password"] = "Password is required."
    return errors