from app import create_app
from extensions import db
from models.user import User
from datetime import datetime, timedelta
from models.quiz import Quiz, QuizQuestion,QuestionAttempt
from models.quiz_attempt import QuizAttempt

def seed_users():
    users = [
        User(
            first_name="Alice",
            last_name="Admin",
            email="admin@example.com",
            role="admin",
            is_approved=True
        ),
        User(
            first_name="Bob",
            last_name="Contributor",
            email="contributor@example.com",
            role="contributor",
            is_approved=True
        ),
        User(
            first_name="Charlie",
            last_name="Learner",
            email="learner@example.com",
            role="learner",
            is_approved=True
        )
    ]

    # Set passwords using the setter
    users[0].password = "admin123"
    users[1].password = "contrib123"
    users[2].password = "learner123"

    db.session.bulk_save_objects(users)
    db.session.commit()

    print("✅ Seeded users with roles: admin, contributor, learner.")

def seed_quizzes():
    """Seed sample quiz data"""
    print("Seeding quiz data...")

    # Get a contributor user (create one if doesn't exist)
    contributor = User.query.filter_by(role='contributor').first()
    if not contributor:
        contributor = User(
            username="quiz_creator",
            email="creator@eduhive.com",
            role="contributor",
            is_active=True
        )
        contributor.set_password("password123")
        db.session.add(contributor)
        db.session.commit()

    # Sample quiz data matching your frontend
    quiz_data = [
        {
            'id': '03',
            'unit': '03',
            'subject': 'CRP',
            'description': 'Customer Relationship Programs quiz covering key concepts and strategies.',
            'issue_date': datetime.utcnow() - timedelta(days=3),
            'deadline': datetime.utcnow() + timedelta(days=2),
            'passing_score': 70,
            'time_limit': 30,
            'max_attempts': 3,
            'questions': [
                {
                    'question_text': 'What is the primary goal of Customer Relationship Programs?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'To increase sales volume',
                        'To build long-term customer loyalty and retention',
                        'To reduce operational costs',
                        'To expand market share'
                    ],
                    'correct_answer': 1,
                    'explanation': 'CRP focuses on building lasting relationships with customers to ensure retention and loyalty.',
                    'points': 2,
                    'difficulty': 'medium'
                },
                {
                    'question_text': 'Which metric is most important for measuring CRP success?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Customer Acquisition Cost (CAC)',
                        'Customer Lifetime Value (CLV)',
                        'Monthly Recurring Revenue (MRR)',
                        'Net Promoter Score (NPS)'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Customer Lifetime Value helps measure the total worth of a customer relationship.',
                    'points': 2,
                    'difficulty': 'hard'
                }
            ]
        },
        {
            'id': '01',
            'unit': '01',
            'subject': 'Introduction to Programming',
            'description': 'Fundamental programming concepts and principles.',
            'issue_date': datetime.utcnow() - timedelta(days=1),
            'deadline': datetime.utcnow() + timedelta(hours=12),
            'passing_score': 70,
            'time_limit': 45,
            'max_attempts': 3,
            'questions': [
                {
                    'question_text': 'What is the primary purpose of a variable in programming?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'To store and manipulate data',
                        'To create loops',
                        'To define functions',
                        'To handle errors'
                    ],
                    'correct_answer': 0,
                    'explanation': 'Variables are used to store data that can be referenced and manipulated in a program.',
                    'points': 1,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'Which of the following is NOT a primitive data type in most programming languages?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Integer',
                        'String',
                        'Array',
                        'Boolean'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Arrays are composite data types that can hold multiple values.',
                    'points': 1,
                    'difficulty': 'medium'
                },
                {
                    'question_text': 'What does IDE stand for?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Internet Development Environment',
                        'Integrated Development Environment',
                        'Interactive Design Editor',
                        'Internal Data Exchange'
                    ],
                    'correct_answer': 1,
                    'explanation': 'IDE stands for Integrated Development Environment, a software application for developers.',
                    'points': 1,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'Which programming paradigm focuses on objects and classes?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Functional Programming',
                        'Procedural Programming',
                        'Object-Oriented Programming',
                        'Logic Programming'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Object-Oriented Programming (OOP) is based on the concept of objects and classes.',
                    'points': 2,
                    'difficulty': 'medium'
                },
                {
                    'question_text': 'What is the time complexity of accessing an element in an array by index?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'O(n)',
                        'O(log n)',
                        'O(1)',
                        'O(n²)'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Array access by index is constant time O(1) operation.',
                    'points': 2,
                    'difficulty': 'hard'
                }
            ]
        },
        {
            'id': '01-2',
            'unit': '01',
            'subject': 'Database',
            'description': 'Database fundamentals and SQL concepts.',
            'issue_date': datetime.utcnow() - timedelta(days=2),
            'deadline': datetime.utcnow() + timedelta(days=5),
            'passing_score': 70,
            'time_limit': 60,
            'max_attempts': 3,
            'questions': [
                {
                    'question_text': 'What does SQL stand for?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Structured Query Language',
                        'Simple Query Language',
                        'Standard Query Language',
                        'System Query Language'
                    ],
                    'correct_answer': 0,
                    'explanation': 'SQL stands for Structured Query Language, used for managing relational databases.',
                    'points': 1,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'Which of the following is a NoSQL database?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'MySQL',
                        'PostgreSQL',
                        'MongoDB',
                        'Oracle'
                    ],
                    'correct_answer': 2,
                    'explanation': 'MongoDB is a popular NoSQL document database.',
                    'points': 2,
                    'difficulty': 'medium'
                },
                {
                    'question_text': 'What is a primary key in a database table?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'A key that can be null',
                        'A unique identifier for each record',
                        'A foreign key reference',
                        'An index for faster searches'
                    ],
                    'correct_answer': 1,
                    'explanation': 'A primary key uniquely identifies each record in a database table.',
                    'points': 2,
                    'difficulty': 'medium'
                }
            ]
        },
        {
            'id': '01-3',
            'unit': '01',
            'subject': 'Networking',
            'description': 'Computer networking fundamentals and protocols.',
            'issue_date': datetime.utcnow() - timedelta(days=5),
            'deadline': datetime.utcnow() + timedelta(days=6),
            'passing_score': 70,
            'time_limit': 40,
            'max_attempts': 3,
            'questions': [
                {
                    'question_text': 'What does TCP stand for?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Transfer Control Protocol',
                        'Transmission Control Protocol',
                        'Transport Control Protocol',
                        'Technical Control Protocol'
                    ],
                    'correct_answer': 1,
                    'explanation': 'TCP stands for Transmission Control Protocol.',
                    'points': 1,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'Which layer of the OSI model handles routing?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Physical Layer',
                        'Data Link Layer',
                        'Network Layer',
                        'Transport Layer'
                    ],
                    'correct_answer': 2,
                    'explanation': 'The Network Layer (Layer 3) handles routing between different networks.',
                    'points': 2,
                    'difficulty': 'medium'
                }
            ]
        },
        {
            'id': '02',
            'unit': '02',
            'subject': 'Security',
            'description': 'Information security principles and practices.',
            'issue_date': datetime.utcnow() - timedelta(days=10),
            'deadline': datetime.utcnow() + timedelta(days=3),
            'passing_score': 75,
            'time_limit': 50,
            'max_attempts': 2,
            'questions': [
                {
                    'question_text': 'What is the primary purpose of encryption?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'To compress data',
                        'To protect data confidentiality',
                        'To improve performance',
                        'To reduce storage space'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Encryption is primarily used to protect data confidentiality by making it unreadable to unauthorized users.',
                    'points': 2,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'Which of the following is a strong password characteristic?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Contains only lowercase letters',
                        'Is based on personal information',
                        'Uses a combination of letters, numbers, and symbols',
                        'Is short and easy to remember'
                    ],
                    'correct_answer': 2,
                    'explanation': 'Strong passwords should include a mix of uppercase, lowercase, numbers, and special characters.',
                    'points': 1,
                    'difficulty': 'easy'
                },
                {
                    'question_text': 'What does CIA stand for in information security?',
                    'question_type': 'multiple_choice',
                    'options': [
                        'Central Intelligence Agency',
                        'Confidentiality, Integrity, Availability',
                        'Computer Information Access',
                        'Cybersecurity Information Analysis'
                    ],
                    'correct_answer': 1,
                    'explanation': 'CIA in information security refers to Confidentiality, Integrity, and Availability - the three pillars of information security.',
                    'points': 2,
                    'difficulty': 'medium'
                }
            ]
        }
    ]

    # Create quizzes and questions
    for quiz_info in quiz_data:
        # Check if quiz already exists
        existing_quiz = Quiz.query.get(quiz_info['id'])
        if existing_quiz:
            print(f"Quiz {quiz_info['id']} already exists, skipping...")
            continue

        # Create quiz
        quiz = Quiz(
            id=quiz_info['id'],
            unit=quiz_info['unit'],
            subject=quiz_info['subject'],
            description=quiz_info['description'],
            issue_date=quiz_info['issue_date'],
            deadline=quiz_info['deadline'],
            passing_score=quiz_info['passing_score'],
            time_limit=quiz_info['time_limit'],
            max_attempts=quiz_info['max_attempts'],
            total_questions=len(quiz_info['questions']),
            created_by=contributor.id,
            is_active=True
        )

        db.session.add(quiz)
        db.session.flush()  # Flush to get the quiz ID

        # Create questions
        for i, question_info in enumerate(quiz_info['questions']):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=question_info['question_text'],
                question_type=question_info['question_type'],
                options=question_info['options'],
                correct_answer=question_info['correct_answer'],
                explanation=question_info['explanation'],
                points=question_info['points'],
                difficulty=question_info['difficulty'],
                order_index=i
            )
            db.session.add(question)

        print(f"Created quiz: {quiz.subject} ({quiz.id})")

    db.session.commit()
    print("Quiz seeding completed!")


def seed_sample_quiz_attempts():
    """Seed sample quiz attempts for testing"""
    print("Seeding sample quiz attempts...")

    # Get some learner users
    learners = User.query.filter_by(role='learner').limit(3).all()

    if not learners:
        # Create sample learners
        for i in range(3):
            learner = User(
                username=f"learner{i+1}",
                email=f"learner{i+1}@eduhive.com",
                role="learner",
                is_active=True,
                total_xp=0,
                current_xp=0
            )
            learner.set_password("password123")
            db.session.add(learner)

        db.session.commit()
        learners = User.query.filter_by(role='learner').limit(3).all()

    # Get some quizzes
    quizzes = Quiz.query.filter_by(is_active=True).all()

    # Create sample attempts
    for quiz in quizzes[:2]:  # Only first 2 quizzes for testing
        for i, learner in enumerate(learners):
            # Create 1-2 attempts per learner per quiz
            attempts_count = 1 if i == 0 else 2

            for attempt_num in range(attempts_count):
                attempt = QuizAttempt(
                    user_id=learner.id,
                    quiz_id=quiz.id,
                    attempt_number=attempt_num + 1,
                    status='completed',
                    time_started=datetime.utcnow() - timedelta(hours=2),
                    time_completed=datetime.utcnow() - timedelta(hours=1),
                    time_taken=1800 + (attempt_num * 300),  # 30-35 minutes
                    ip_address='127.0.0.1',
                    user_agent='Mozilla/5.0 Test Browser'
                )

                db.session.add(attempt)
                db.session.flush()

                # Create question attempts
                correct_count = 0
                total_points = 0
                max_points = 0

                for question in quiz.questions:
                    # Simulate different performance levels
                    if i == 0:  # Good performer
                        is_correct = True if attempt_num == 0 else (question.order_index % 2 == 0)
                    elif i == 1:  # Average performer
                        is_correct = question.order_index % 3 != 0
                    else:  # Struggling performer
                        is_correct = question.order_index % 4 == 0

                    user_answer = question.correct_answer if is_correct else (question.correct_answer + 1) % len(question.options)
                    points_earned = question.points if is_correct else 0

                    question_attempt = QuestionAttempt(
                        quiz_attempt_id=attempt.id,
                        question_id=question.id,
                        user_answer=str(user_answer),
                        is_correct=is_correct,
                        points_earned=points_earned,
                        time_spent=60 + (question.order_index * 20)  # 1-5 minutes per question
                    )

                    db.session.add(question_attempt)

                    if is_correct:
                        correct_count += 1
                    total_points += points_earned
                    max_points += question.points

                # Update attempt with calculated scores
                attempt.correct_answers = correct_count
                attempt.total_questions = len(quiz.questions)
                attempt.total_points = total_points
                attempt.max_points = max_points
                attempt.score = (total_points / max_points) * 100 if max_points > 0 else 0

                # Award XP if passed
                if attempt.score >= quiz.passing_score:
                    xp_earned = quiz.total_questions * 10
                    learner.total_xp += xp_earned
                    learner.current_xp += xp_earned

    db.session.commit()
    print("Sample quiz attempts seeding completed!")


def seed_all_quiz_data():
    """Seed all quiz-related data"""
    seed_quizzes()
    seed_sample_quiz_attempts()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Drop and recreate tables for fresh seeding — only use in dev
        db.drop_all()
        db.create_all()

        seed_users()
        seed_all_quiz_data()