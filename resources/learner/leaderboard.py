
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from core.models.user import User
from core.models.learner_activity import LearnerActivity
from core.models.progress import Progress
from sqlalchemy import func
from core.extensions import db

bp = Blueprint("learner_leaderboard", __name__, url_prefix="/learner/leaderboard")

@bp.route("/", methods=["GET"])
@jwt_required()
@role_required("learner")
def get_leaderboard():
    """
    Returns leaderboard with:
    - Pagination
    - Search, month, activity filters
    - Global rank (based on score)
    - Most common activity per learner
    - Max path progress per learner
    """

    # Query params
    search = request.args.get("search", "").lower()
    month = request.args.get("month", "all")
    activity_filter = request.args.get("activity", "all")
    sort = request.args.get("sort", "desc")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    # Global rank mapping
    all_learners = User.query.filter_by(role="learner").order_by(User.score.desc()).all()
    global_ranks = {u.id: i + 1 for i, u in enumerate(all_learners)}

    # Base query
    query = User.query.filter_by(role="learner")

    if search:
        query = query.filter(func.lower(User.username).like(f"%{search}%"))

    if month != "all":
        try:
            year, mon = month.split("-")
            query = query.filter(func.strftime("%Y-%m", User.joined) == f"{year}-{mon}")
        except ValueError:
            return jsonify({"error": "Invalid month format"}), 400

    if activity_filter != "all":
        query = query.join(LearnerActivity).filter(LearnerActivity.type == activity_filter)

    # Sorting
    query = query.order_by(User.score.asc() if sort == "asc" else User.score.desc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    # Get most common activity per user
    activity_counts = (
        db.session.query(
            LearnerActivity.learner_id,
            LearnerActivity.type,
            func.count(LearnerActivity.id).label("count")
        )
        .group_by(LearnerActivity.learner_id, LearnerActivity.type)
        .subquery()
    )

    most_common_activity = (
        db.session.query(activity_counts.c.learner_id, activity_counts.c.type)
        .join(
            db.session.query(
                activity_counts.c.learner_id,
                func.max(activity_counts.c.count).label("max_count")
            ).group_by(activity_counts.c.learner_id).subquery(),
            onclause=(
                (activity_counts.c.learner_id == db.literal_column("anon_1.learner_id")) &
                (activity_counts.c.count == db.literal_column("anon_1.max_count"))
            )
        )
    ).all()

    activity_map = {row.learner_id: row.type for row in most_common_activity}

    # Get top path progress per user
    progress_query = (
        db.session.query(
            Progress.learner_id,
            func.max(Progress.progress).label("max_progress")
        )
        .group_by(Progress.learner_id)
        .all()
    )

    progress_map = {row.learner_id: round(row.max_progress, 2) for row in progress_query}

    # Build response
    leaderboard = []
    for user in users:
        leaderboard.append({
            "id": user.id,
            "username": user.username,
            "score": user.score,
            "rank": global_ranks.get(user.id),
            "avatar": getattr(user, "avatar_url", None),
            "joined": user.joined.strftime("%Y-%m") if user.joined else None,
            "activity": activity_map.get(user.id),
            "top_progress": progress_map.get(user.id, 0.0)
        })

    return jsonify({
        "leaderboard": leaderboard,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200
