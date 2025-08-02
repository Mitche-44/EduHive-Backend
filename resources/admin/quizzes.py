from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from models.quiz import Quiz, QuizQuestion
from models.quiz_attempt import QuizAttempt
from models.user import User
from utils.decorators import admin_required
from sqlalchemy import func, desc

class AdminQuizzesOverviewResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get comprehensive quiz overview for admin dashboard"""
        try:
            # Get query parameters
            days = request.args.get('days', 30, type=int)
            date_from = datetime.utcnow() - timedelta(days=days)

            # Basic statistics
            total_quizzes = Quiz.query.count()
            active_quizzes = Quiz.query.filter_by(is_active=True).count()
            total_attempts = QuizAttempt.query.filter_by(status='completed').count()
            recent_attempts = QuizAttempt.query.filter(
                QuizAttempt.time_completed >= date_from,
                QuizAttempt.status == 'completed'
            ).count()

            # Average scores and pass rates
            completed_attempts = QuizAttempt.query.filter_by(status='completed').all()
            if completed_attempts:
                avg_score = sum(a.score for a in completed_attempts) / len(completed_attempts)
                total_passed = len([a for a in completed_attempts if a.is_passed])
                overall_pass_rate = (total_passed / len(completed_attempts)) * 100
            else:
                avg_score = 0
                overall_pass_rate = 0

            # Top performing quizzes
            top_quizzes = db.session.query(
                Quiz.id,
                Quiz.subject,
                Quiz.unit,
                func.count(QuizAttempt.id).label('attempt_count'),
                func.avg(QuizAttempt.score).label('avg_score')
            ).join(QuizAttempt).filter(
                QuizAttempt.status == 'completed'
            ).group_by(Quiz.id).order_by(
                desc('attempt_count')
            ).limit(10).all()

            # Recent quiz activity
            recent_quizzes = Quiz.query.order_by(desc(Quiz.created_at)).limit(5).all()

            # Quiz creation trends (last 30 days)
            quiz_trends = []
            for i in range(30):
                date = datetime.utcnow().date() - timedelta(days=i)
                count = Quiz.query.filter(
                    func.date(Quiz.created_at) == date
                ).count()
                quiz_trends.append({
                    'date': date.isoformat(),
                    'count': count
                })

            overview_data = {
                'statistics': {
                    'total_quizzes': total_quizzes,
                    'active_quizzes': active_quizzes,
                    'total_attempts': total_attempts,
                    'recent_attempts': recent_attempts,
                    'average_score': round(avg_score, 2),
                    'overall_pass_rate': round(overall_pass_rate, 2)
                },
                'top_performing_quizzes': [
                    {
                        'id': q.id,
                        'subject': q.subject,
                        'unit': q.unit,
                        'attempt_count': q.attempt_count,
                        'average_score': round(float(q.avg_score), 2)
                    } for q in top_quizzes
                ],
                'recent_quizzes': [q.to_dict() for q in recent_quizzes],
                'creation_trends': quiz_trends[::-1]  # Reverse to show oldest first
            }

            return {
                'success': True,
                'data': overview_data
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz overview: {str(e)}'
            }, 500


class AdminQuizzesListResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get all quizzes with admin-level details"""
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            unit = request.args.get('unit')
            subject = request.args.get('subject')
            status = request.args.get('status')  # 'active', 'inactive', 'all'
            creator_id = request.args.get('creator_id', type=int)

            # Base query
            query = Quiz.query

            # Apply filters
            if unit:
                query = query.filter_by(unit=unit)
            if subject:
                query = query.filter(Quiz.subject.ilike(f'%{subject}%'))
            if status and status != 'all':
                is_active = status == 'active'
                query = query.filter_by(is_active=is_active)
            if creator_id:
                query = query.filter_by(created_by=creator_id)

            # Paginate
            paginated_quizzes = query.order_by(desc(Quiz.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Enhance quiz data with statistics
            quiz_data = []
            for quiz in paginated_quizzes.items:
                attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id, status='completed').all()

                quiz_info = quiz.to_dict()
                quiz_info.update({
                    'creator_name': quiz.creator.username,
                    'total_attempts': len(attempts),
                    'unique_users': len(set(a.user_id for a in attempts)),
                    'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
                    'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100 if attempts else 0,
                    'total_questions': len(quiz.questions)
                })

                quiz_data.append(quiz_info)

            return {
                'success': True,
                'data': quiz_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated_quizzes.total,
                    'pages': paginated_quizzes.pages,
                    'has_next': paginated_quizzes.has_next,
                    'has_prev': paginated_quizzes.has_prev
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quizzes: {str(e)}'
            }, 500


class AdminQuizDetailResource(Resource):
    @jwt_required()
    @admin_required
    def get(self, quiz_id):
        """Get detailed quiz information for admin"""
        try:
            quiz = Quiz.query.get_or_404(quiz_id)

            # Get all attempts for this quiz
            attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id, status='completed').all()

            # Get question-level analytics
            question_analytics = []
            for question in quiz.questions:
                question_attempts = []
                for attempt in attempts:
                    qa = next((qa for qa in attempt.question_attempts if qa.question_id == question.id), None)
                    if qa:
                        question_attempts.append(qa)

                if question_attempts:
                    correct_count = sum(1 for qa in question_attempts if qa.is_correct)
                    question_analytics.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'total_attempts': len(question_attempts),
                        'correct_answers': correct_count,
                        'accuracy_rate': (correct_count / len(question_attempts)) * 100
                    })

            # Recent attempts
            recent_attempts = QuizAttempt.query.filter_by(
                quiz_id=quiz_id, status='completed'
            ).order_by(desc(QuizAttempt.time_completed)).limit(10).all()

            quiz_data = quiz.to_dict()
            quiz_data.update({
                'creator_name': quiz.creator.username,
                'creator_email': quiz.creator.email,
                'questions': [q.to_dict() for q in quiz.questions],
                'total_attempts': len(attempts),
                'unique_users': len(set(a.user_id for a in attempts)),
                'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
                'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100 if attempts else 0,
                'question_analytics': question_analytics,
                'recent_attempts': [
                    {
                        **attempt.get_attempt_summary(),
                        'user_name': attempt.user.username,
                        'user_email': attempt.user.email
                    } for attempt in recent_attempts
                ]
            })

            return {
                'success': True,
                'data': quiz_data
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz details: {str(e)}'
            }, 500

    @jwt_required()
    @admin_required
    def put(self, quiz_id):
        """Update quiz (admin can override some restrictions)"""
        try:
            data = request.get_json()
            quiz = Quiz.query.get_or_404(quiz_id)

            # Admin can update more fields than contributors
            if 'subject' in data:
                quiz.subject = data['subject']
            if 'description' in data:
                quiz.description = data['description']
            if 'deadline' in data:
                try:
                    quiz.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    quiz.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
            if 'passing_score' in data:
                quiz.passing_score = data['passing_score']
            if 'time_limit' in data:
                quiz.time_limit = data['time_limit']
            if 'max_attempts' in data:
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
    @admin_required
    def delete(self, quiz_id):
        """Delete quiz (admin can delete even with attempts)"""
        try:
            quiz = Quiz.query.get_or_404(quiz_id)

            # Get confirmation from request data
            data = request.get_json() or {}
            force_delete = data.get('force_delete', False)

            # Check if quiz has attempts
            has_attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).first() is not None

            if has_attempts and not force_delete:
                return {
                    'success': False,
                    'message': 'Quiz has existing attempts. Use force_delete=true to confirm deletion.',
                    'requires_confirmation': True
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


class AdminQuizAttemptsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self, quiz_id):
        """Get all attempts for a specific quiz"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            quiz = Quiz.query.get_or_404(quiz_id)

            # Get paginated attempts
            paginated_attempts = QuizAttempt.query.filter_by(
                quiz_id=quiz_id, status='completed'
            ).order_by(desc(QuizAttempt.time_completed)).paginate(
                page=page, per_page=per_page, error_out=False
            )

            attempts_data = []
            for attempt in paginated_attempts.items:
                attempt_info = attempt.get_attempt_summary()
                attempt_info.update({
                    'user_name': attempt.user.username,
                    'user_email': attempt.user.email,
                    'ip_address': attempt.ip_address,
                    'user_agent': attempt.user_agent
                })
                attempts_data.append(attempt_info)

            return {
                'success': True,
                'data': {
                    'quiz': quiz.to_dict(),
                    'attempts': attempts_data
                },
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated_attempts.total,
                    'pages': paginated_attempts.pages,
                    'has_next': paginated_attempts.has_next,
                    'has_prev': paginated_attempts.has_prev
                }
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching quiz attempts: {str(e)}'
            }, 500


class AdminQuizReportsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Generate comprehensive quiz reports"""
        try:
            report_type = request.args.get('type', 'summary')  # summary, detailed, trends
            days = request.args.get('days', 30, type=int)

            date_from = datetime.utcnow() - timedelta(days=days)

            if report_type == 'summary':
                # Summary report
                total_quizzes = Quiz.query.count()
                active_quizzes = Quiz.query.filter_by(is_active=True).count()

                attempts_in_period = QuizAttempt.query.filter(
                    QuizAttempt.time_completed >= date_from,
                    QuizAttempt.status == 'completed'
                ).all()

                report_data = {
                    'period': f'Last {days} days',
                    'total_quizzes': total_quizzes,
                    'active_quizzes': active_quizzes,
                    'attempts_in_period': len(attempts_in_period),
                    'unique_users_in_period': len(set(a.user_id for a in attempts_in_period)),
                    'average_score_in_period': sum(a.score for a in attempts_in_period) / len(attempts_in_period) if attempts_in_period else 0,
                    'pass_rate_in_period': len([a for a in attempts_in_period if a.is_passed]) / len(attempts_in_period) * 100 if attempts_in_period else 0
                }

            elif report_type == 'trends':
                # Trends report
                daily_data = []
                for i in range(days):
                    date = datetime.utcnow().date() - timedelta(days=i)
                    attempts = QuizAttempt.query.filter(
                        func.date(QuizAttempt.time_completed) == date,
                        QuizAttempt.status == 'completed'
                    ).all()

                    daily_data.append({
                        'date': date.isoformat(),
                        'attempts': len(attempts),
                        'unique_users': len(set(a.user_id for a in attempts)),
                        'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
                        'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100 if attempts else 0
                    })

                report_data = {
                    'period': f'Last {days} days',
                    'daily_trends': daily_data[::-1]  # Reverse to show oldest first
                }

            else:  # detailed
                # Detailed report
                quiz_performance = []
                quizzes = Quiz.query.filter_by(is_active=True).all()

                for quiz in quizzes:
                    attempts = QuizAttempt.query.filter(
                        QuizAttempt.quiz_id == quiz.id,
                        QuizAttempt.time_completed >= date_from,
                        QuizAttempt.status == 'completed'
                    ).all()

                    if attempts:
                        quiz_performance.append({
                            'quiz_id': quiz.id,
                            'subject': quiz.subject,
                            'unit': quiz.unit,
                            'attempts': len(attempts),
                            'unique_users': len(set(a.user_id for a in attempts)),
                            'average_score': sum(a.score for a in attempts) / len(attempts),
                            'pass_rate': len([a for a in attempts if a.is_passed]) / len(attempts) * 100,
                            'average_time': sum(a.time_taken or 0 for a in attempts) / len(attempts)
                        })

                report_data = {
                    'period': f'Last {days} days',
                    'quiz_performance': sorted(quiz_performance, key=lambda x: x['attempts'], reverse=True)
                }

            return {
                'success': True,
                'data': report_data,
                'generated_at': datetime.utcnow().isoformat()
            }, 200

        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }, 500