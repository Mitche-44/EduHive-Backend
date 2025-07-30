from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from models.quiz import Quiz, QuizQuestion
from models.quiz_attempt import QuizAttempt
from models.module import Module
from utils.decorators import contributor_required
from utils.validators import validate_quiz_data, validate_question_data

class ContributorQuizzesResource(Resource):
    @jwt_required()
    @contributor_required
    def get(self):
        """Get all quizzes created by the contributor"""
        try:
            current_user_id = get_jwt_identity()

            # Get query parameters
            unit = request.args.get('unit')
            subject = request.args.get('subject')
            status = request.args.get('status')  # 'active', 'inactive', 'all'

            # Base query
            query = Quiz.query.filter_by(created_by=current_user_id)

            # Apply filters
            if unit:
                query = query.filter_by(unit=unit)
            if subject:
                query = query.filter(Quiz.subject.ilike(f'%{subject}%'))
            if status and status != 'all':
                is_active = status == 'active'
                query = query.filter_by(is_active=is_active)

            quizzes = query.order_by(Quiz.created_at.desc()).all()

            # Enhance quiz data with statistics
            quiz_data = []
            for quiz in quizzes:
                attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id, status='completed').all()

                quiz_info = quiz.to_dict()
                quiz_info.update({
                    'total_attempts': len(attempts),
                    'total_questions': len(quiz.questions),
                    'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
                    'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100 if attempts else 0
                })

                quiz_data.append(quiz_info)

            return {
                'success': True,
                'data': quiz_data,
                'total': len(quiz_data)
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quizzes: {str(e)}'
            }, 500

    @jwt_required()
    @contributor_required
    def post(self):
        """Create a new quiz"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # Validate quiz data
            validation_errors = validate_quiz_data(data)
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation errors',
                    'errors': validation_errors
                }, 400

            # Parse deadline
            try:
                deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
                except ValueError:
                    return {
                        'success': False,
                        'message': 'Invalid deadline format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS'
                    }, 400

            # Parse issue_date if provided
            issue_date = datetime.utcnow()
            if data.get('issue_date'):
                try:
                    issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
                    except ValueError:
                        return {
                            'success': False,
                            'message': 'Invalid issue date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS'
                        }, 400

            # Check if module exists (if provided)
            module_id = data.get('module_id')
            if module_id:
                module = Module.query.get(module_id)
                if not module:
                    return {
                        'success': False,
                        'message': 'Module not found'
                    }, 404

            # Create quiz
            quiz = Quiz(
                id=data['id'],
                unit=data['unit'],
                subject=data['subject'],
                description=data.get('description'),
                issue_date=issue_date,
                deadline=deadline,
                passing_score=data.get('passing_score', 70),
                time_limit=data.get('time_limit'),
                max_attempts=data.get('max_attempts', 3),
                module_id=module_id,
                created_by=current_user_id
            )

            db.session.add(quiz)
            db.session.commit()

            return {
                'success': True,
                'data': quiz.to_dict(),
                'message': 'Quiz created successfully'
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating quiz: {str(e)}'
            }, 500


class ContributorQuizDetailResource(Resource):
    @jwt_required()
    @contributor_required
    def get(self, quiz_id):
        """Get detailed quiz information for contributor"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            # Get quiz with all questions and statistics
            attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id, status='completed').all()

            quiz_data = quiz.to_dict()
            quiz_data.update({
                'questions': [q.to_dict() for q in quiz.questions],
                'total_attempts': len(attempts),
                'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
                'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100 if attempts else 0,
                'recent_attempts': [a.get_attempt_summary() for a in attempts[-5:]]
            })

            return {
                'success': True,
                'data': quiz_data
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz: {str(e)}'
            }, 500

    @jwt_required()
    @contributor_required
    def put(self, quiz_id):
        """Update quiz information"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            # Check if quiz has attempts (limit updates if it does)
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None

            # Update allowed fields
            if 'subject' in data:
                quiz.subject = data['subject']
            if 'description' in data:
                quiz.description = data['description']
            if 'deadline' in data and not has_attempts:
                try:
                    quiz.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    quiz.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
            if 'passing_score' in data and not has_attempts:
                quiz.passing_score = data['passing_score']
            if 'time_limit' in data:
                quiz.time_limit = data['time_limit']
            if 'max_attempts' in data and not has_attempts:
                quiz.max_attempts = data['max_attempts']
            if 'is_active' in data:
                quiz.is_active = data['is_active']

            quiz.updated_at = datetime.utcnow()
            db.session.commit()

            return {
                'success': True,
                'data': quiz.to_dict(),
                'message': 'Quiz updated successfully'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating quiz: {str(e)}'
            }, 500

    @jwt_required()
    @contributor_required
    def delete(self, quiz_id):
        """Delete quiz (only if no attempts)"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            # Check if quiz has attempts
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None
            if has_attempts:
                return {
                    'success': False,
                    'message': 'Cannot delete quiz with existing attempts. Deactivate instead.'
                }, 400

            db.session.delete(quiz)
            db.session.commit()

            return {
                'success': True,
                'message': 'Quiz deleted successfully'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting quiz: {str(e)}'
            }, 500


class QuizQuestionsResource(Resource):
    @jwt_required()
    @contributor_required
    def post(self, quiz_id):
        """Add questions to quiz"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            # Check if quiz has attempts (prevent adding questions)
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None
            if has_attempts:
                return {
                    'success': False,
                    'message': 'Cannot modify questions for quiz with existing attempts'
                }, 400

            questions_data = data.get('questions', [])
            if not questions_data:
                return {
                    'success': False,
                    'message': 'No questions provided'
                }, 400

            added_questions = []
            for i, question_data in enumerate(questions_data):
                # Validate question data
                validation_errors = validate_question_data(question_data)
                if validation_errors:
                    return {
                        'success': False,
                        'message': f'Validation errors in question {i+1}',
                        'errors': validation_errors
                    }, 400

                question = QuizQuestion(
                    quiz_id=quiz_id,
                    question_text=question_data['question_text'],
                    question_type=question_data.get('question_type', 'multiple_choice'),
                    options=question_data.get('options'),
                    correct_answer=question_data.get('correct_answer'),
                    correct_answer_text=question_data.get('correct_answer_text'),
                    explanation=question_data.get('explanation'),
                    points=question_data.get('points', 1),
                    difficulty=question_data.get('difficulty', 'medium'),
                    order_index=question_data.get('order_index', i)
                )

                db.session.add(question)
                added_questions.append(question)

            # Update quiz total questions count
            quiz.total_questions = len(quiz.questions) + len(added_questions)
            quiz.updated_at = datetime.utcnow()

            db.session.commit()

            return {
                'success': True,
                'data': {
                    'questions_added': len(added_questions),
                    'total_questions': quiz.total_questions,
                    'questions': [q.to_dict() for q in added_questions]
                },
                'message': f'{len(added_questions)} questions added successfully'
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error adding questions: {str(e)}'
            }, 500


class QuizQuestionDetailResource(Resource):
    @jwt_required()
    @contributor_required
    def put(self, quiz_id, question_id):
        """Update a specific question"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            question = QuizQuestion.query.filter_by(id=question_id, quiz_id=quiz_id).first()
            if not question:
                return {
                    'success': False,
                    'message': 'Question not found'
                }, 404

            # Check if quiz has attempts
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None
            if has_attempts:
                return {
                    'success': False,
                    'message': 'Cannot modify questions for quiz with existing attempts'
                }, 400

            # Update question fields
            if 'question_text' in data:
                question.question_text = data['question_text']
            if 'options' in data:
                question.options = data['options']
            if 'correct_answer' in data:
                question.correct_answer = data['correct_answer']
            if 'correct_answer_text' in data:
                question.correct_answer_text = data['correct_answer_text']
            if 'explanation' in data:
                question.explanation = data['explanation']
            if 'points' in data:
                question.points = data['points']
            if 'difficulty' in data:
                question.difficulty = data['difficulty']
            if 'order_index' in data:
                question.order_index = data['order_index']

            db.session.commit()

            return {
                'success': True,
                'data': question.to_dict(),
                'message': 'Question updated successfully'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating question: {str(e)}'
            }, 500

    @jwt_required()
    @contributor_required
    def delete(self, quiz_id, question_id):
        """Delete a specific question"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            question = QuizQuestion.query.filter_by(id=question_id, quiz_id=quiz_id).first()
            if not question:
                return {
                    'success': False,
                    'message': 'Question not found'
                }, 404

            # Check if quiz has attempts
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None
            if has_attempts:
                return {
                    'success': False,
                    'message': 'Cannot delete questions for quiz with existing attempts'
                }, 400

            db.session.delete(question)

            # Update quiz total questions count
            quiz.total_questions = len(quiz.questions) - 1
            quiz.updated_at = datetime.utcnow()

            db.session.commit()

            return {
                'success': True,
                'message': 'Question deleted successfully'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting question: {str(e)}'
            }, 500


class QuizAnalyticsResource(Resource):
    @jwt_required()
    @contributor_required
    def get(self, quiz_id):
        """Get detailed analytics for a quiz"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.filter_by(id=quiz_id, created_by=current_user_id).first()
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz not found'
                }, 404

            # Get all completed attempts
            attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id, status='completed').all()

            if not attempts:
                return {
                    'success': True,
                    'data': {
                        'quiz_id': quiz_id,
                        'total_attempts': 0,
                        'analytics': {}
                    }
                }, 200

            # Calculate analytics
            scores = [a.score for a in attempts]
            total_attempts = len(attempts)
            passed_attempts = len([a for a in attempts if a.is_passed])

            analytics = {
                'total_attempts': total_attempts,
                'unique_users': len(set(a.user_id for a in attempts)),
                'pass_rate': (passed_attempts / total_attempts) * 100,
                'average_score': sum(scores) / total_attempts,
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'score_distribution': {
                    'A (90-100)': len([s for s in scores if s >= 90]),
                    'B (80-89)': len([s for s in scores if 80 <= s < 90]),
                    'C (70-79)': len([s for s in scores if 70 <= s < 80]),
                    'D (60-69)': len([s for s in scores if 60 <= s < 70]),
                    'F (0-59)': len([s for s in scores if s < 60])
                },
                'average_time_taken': sum(a.time_taken or 0 for a in attempts) / total_attempts,
                'question_analytics': []
            }

            # Question-level analytics
            for question in quiz.questions:
                question_attempts = []
                for attempt in attempts:
                    qa = next((qa for qa in attempt.question_attempts if qa.question_id == question.id), None)
                    if qa:
                        question_attempts.append(qa)

                if question_attempts:
                    correct_count = sum(1 for qa in question_attempts if qa.is_correct)
                    question_analytics = {
                        'question_id': question.id,
                        'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                        'total_attempts': len(question_attempts),
                        'correct_answers': correct_count,
                        'accuracy_rate': (correct_count / len(question_attempts)) * 100,
                        'difficulty_rating': 'Easy' if (correct_count / len(question_attempts)) > 0.8 else 'Hard' if (correct_count / len(question_attempts)) < 0.5 else 'Medium'
                    }
                    analytics['question_analytics'].append(question_analytics)

            return {
                'success': True,
                'data': {
                    'quiz_id': quiz_id,
                    'quiz_title': quiz.subject,
                    'analytics': analytics
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching analytics: {str(e)}'
            }, 500