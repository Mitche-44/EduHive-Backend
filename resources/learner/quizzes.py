from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from models.quiz import Quiz, QuizQuestion, QuestionAttempt
from models.quiz_attempt import QuizAttempt
from models.user import User
from utils.decorators import learner_required
from utils.validators import validate_quiz_submission
from utils.helpers import get_client_ip, get_user_agent

class QuizzesListResource(Resource):
    @jwt_required()
    @learner_required
    def get(self):
        """Get all available quizzes for learner"""
        try:
            current_user_id = get_jwt_identity()

            # Get query parameters
            unit = request.args.get('unit')
            subject = request.args.get('subject')
            status = request.args.get('status')  # 'pending', 'completed', 'all'

            # Base query
            query = Quiz.query.filter_by(is_active=True)

            # Apply filters
            if unit:
                query = query.filter_by(unit=unit)
            if subject:
                query = query.filter(Quiz.subject.ilike(f'%{subject}%'))

            quizzes = query.order_by(Quiz.deadline.asc()).all()

            # Enhance quiz data with user-specific information
            quiz_data = []
            for quiz in quizzes:
                user_attempts = quiz.get_user_attempts(current_user_id)
                best_score = quiz.get_user_best_score(current_user_id)
                can_attempt, message = quiz.can_user_attempt(current_user_id)

                quiz_info = quiz.to_dict()
                quiz_info.update({
                    'user_attempts_count': len(user_attempts),
                    'user_best_score': best_score,
                    'can_attempt': can_attempt,
                    'attempt_message': message,
                    'status': 'Submitted' if user_attempts and any(a.status == 'completed' for a in user_attempts) else 'Pending',
                    'is_completed': best_score is not None and best_score >= quiz.passing_score
                })

                # Filter by status if requested
                if status and status != 'all':
                    if status == 'pending' and quiz_info['status'] != 'Pending':
                        continue
                    elif status == 'completed' and quiz_info['status'] != 'Submitted':
                        continue

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


class QuizDetailResource(Resource):
    @jwt_required()
    @learner_required
    def get(self, quiz_id):
        """Get detailed quiz information including questions"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.get_or_404(quiz_id)

            if not quiz.is_active:
                return {
                    'success': False,
                    'message': 'Quiz is not available'
                }, 404

            # Check if user can access this quiz
            can_attempt, message = quiz.can_user_attempt(current_user_id)
            user_attempts = quiz.get_user_attempts(current_user_id)

            # Get quiz questions (without correct answers)
            questions_data = []
            for question in quiz.questions:
                question_data = {
                    'id': question.id,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'options': question.options,
                    'points': question.points,
                    'difficulty': question.difficulty,
                    'order_index': question.order_index
                }
                questions_data.append(question_data)

            # Sort questions by order
            questions_data.sort(key=lambda x: x['order_index'])

            quiz_data = quiz.to_dict()
            quiz_data.update({
                'questions': questions_data,
                'user_attempts_count': len(user_attempts),
                'user_best_score': quiz.get_user_best_score(current_user_id),
                'can_attempt': can_attempt,
                'attempt_message': message,
                'user_attempts': [attempt.get_attempt_summary() for attempt in user_attempts]
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


class QuizAttemptResource(Resource):
    @jwt_required()
    @learner_required
    def post(self, quiz_id):
        """Start a new quiz attempt"""
        try:
            current_user_id = get_jwt_identity()

            quiz = Quiz.query.get_or_404(quiz_id)

            # Validate if user can attempt
            can_attempt, message = quiz.can_user_attempt(current_user_id)
            if not can_attempt:
                return {
                    'success': False,
                    'message': message
                }, 400

            # Create new attempt
            user_attempts = quiz.get_user_attempts(current_user_id)
            attempt_number = len(user_attempts) + 1

            new_attempt = QuizAttempt(
                user_id=current_user_id,
                quiz_id=quiz_id,
                attempt_number=attempt_number,
                status='in_progress',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.add(new_attempt)
            db.session.commit()

            return {
                'success': True,
                'data': {
                    'attempt_id': new_attempt.id,
                    'attempt_number': attempt_number,
                    'time_started': new_attempt.time_started.isoformat(),
                    'time_limit': quiz.time_limit
                },
                'message': 'Quiz attempt started successfully'
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error starting quiz attempt: {str(e)}'
            }, 500


class QuizSubmissionResource(Resource):
    @jwt_required()
    @learner_required
    def post(self, quiz_id, attempt_id):
        """Submit quiz answers"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            # Validate submission data
            validation_errors = validate_quiz_submission(data)
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation errors',
                    'errors': validation_errors
                }, 400

            # Get quiz attempt
            attempt = QuizAttempt.query.filter_by(
                id=attempt_id,
                quiz_id=quiz_id,
                user_id=current_user_id,
                status='in_progress'
            ).first()

            if not attempt:
                return {
                    'success': False,
                    'message': 'Quiz attempt not found or already completed'
                }, 404

            quiz = attempt.quiz
            answers = data.get('answers', {})

            # Process each answer
            for question_id, user_answer in answers.items():
                question = QuizQuestion.query.get(int(question_id))
                if not question or question.quiz_id != quiz_id:
                    continue

                # Check if answer already exists (prevent duplicate submissions)
                existing_answer = QuestionAttempt.query.filter_by(
                    quiz_attempt_id=attempt_id,
                    question_id=question_id
                ).first()

                if existing_answer:
                    continue

                # Create question attempt
                is_correct = question.is_correct_answer(user_answer)
                points_earned = question.points if is_correct else 0

                question_attempt = QuestionAttempt(
                    quiz_attempt_id=attempt_id,
                    question_id=question_id,
                    user_answer=str(user_answer),
                    is_correct=is_correct,
                    points_earned=points_earned
                )

                db.session.add(question_attempt)

            # Submit the attempt
            final_score = attempt.submit_attempt()

            # Award XP to user if passed
            user = User.query.get(current_user_id)
            xp_earned = 0
            if attempt.is_passed:
                xp_earned = quiz.total_questions * 10  # 10 XP per question
                user.total_xp += xp_earned
                user.current_xp += xp_earned

            db.session.commit()

            return {
                'success': True,
                'data': {
                    'attempt_id': attempt_id,
                    'score': final_score,
                    'grade': attempt.grade,
                    'is_passed': attempt.is_passed,
                    'correct_answers': attempt.correct_answers,
                    'total_questions': attempt.total_questions,
                    'time_taken': attempt.time_taken,
                    'xp_earned': xp_earned
                },
                'message': 'Quiz submitted successfully'
            }, 200

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error submitting quiz: {str(e)}'
            }, 500


class QuizResultResource(Resource):
    @jwt_required()
    @learner_required
    def get(self, quiz_id, attempt_id):
        """Get detailed quiz results"""
        try:
            current_user_id = get_jwt_identity()

            attempt = QuizAttempt.query.filter_by(
                id=attempt_id,
                quiz_id=quiz_id,
                user_id=current_user_id,
                status='completed'
            ).first()

            if not attempt:
                return {
                    'success': False,
                    'message': 'Quiz result not found'
                }, 404

            # Get detailed results
            question_results = []
            for qa in attempt.question_attempts:
                question_result = {
                    'question_id': qa.question_id,
                    'question_text': qa.question.question_text,
                    'options': qa.question.options,
                    'user_answer': qa.user_answer,
                    'correct_answer': qa.question.correct_answer,
                    'is_correct': qa.is_correct,
                    'points_earned': qa.points_earned,
                    'points_possible': qa.question.points,
                    'explanation': qa.question.explanation
                }
                question_results.append(question_result)

            result_data = attempt.get_attempt_summary()
            result_data['question_results'] = question_results

            return {
                'success': True,
                'data': result_data
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz result: {str(e)}'
            }, 500


class UserQuizStatsResource(Resource):
    @jwt_required()
    @learner_required
    def get(self):
        """Get user's quiz statistics"""
        try:
            current_user_id = get_jwt_identity()

            # Get all user's completed attempts
            completed_attempts = QuizAttempt.query.filter_by(
                user_id=current_user_id,
                status='completed'
            ).all()

            if not completed_attempts:
                return {
                    'success': True,
                    'data': {
                        'total_quizzes_taken': 0,
                        'total_quizzes_passed': 0,
                        'average_score': 0,
                        'success_rate': 0,
                        'recent_attempts': []
                    }
                }, 200

            # Calculate statistics
            total_attempts = len(completed_attempts)
            passed_attempts = [a for a in completed_attempts if a.is_passed]
            total_passed = len(passed_attempts)

            average_score = sum(a.score for a in completed_attempts) / total_attempts
            success_rate = (total_passed / total_attempts) * 100

            # Get recent attempts (last 5)
            recent_attempts = sorted(completed_attempts, key=lambda x: x.time_completed, reverse=True)[:5]
            recent_data = [attempt.get_attempt_summary() for attempt in recent_attempts]

            stats = {
                'total_quizzes_taken': total_attempts,
                'total_quizzes_passed': total_passed,
                'average_score': round(average_score, 2),
                'success_rate': round(success_rate, 2),
                'recent_attempts': recent_data
            }

            return {
                'success': True,
                'data': stats
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz stats: {str(e)}'
            }, 500