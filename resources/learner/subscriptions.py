from flask import Blueprint, request, jsonify
from extensions import db
from models.subscription import Subscription
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

subscription_bp = Blueprint("subscription", __name__, url_prefix="/api/subscription")

@subscription_bp.route("/subscribe", methods=["POST"])
@jwt_required()
def subscribe():
    data = request.get_json()
    plan = data.get("plan")
    billing_cycle = data.get("billing_cycle")

    if plan not in ["Free", "Basic", "Pro", "Elite"]:
        return jsonify({"error": "Invalid plan"}), 400

    if billing_cycle not in ["monthly", "yearly"]:
        return jsonify({"error": "Invalid billing cycle"}), 400

    user_id = get_jwt_identity()

    # Calculate end date
    duration = timedelta(days=365 if billing_cycle == "yearly" else 30)
    end_date = datetime.utcnow() + duration

    # Check if already subscribed
    existing = Subscription.query.filter_by(user_id=user_id, active=True).first()
    if existing:
        existing.active = False
        db.session.commit()

    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        billing_cycle=billing_cycle,
        start_date=datetime.utcnow(),
        end_date=end_date,
        active=True
    )
    db.session.add(subscription)
    db.session.commit()

    return jsonify({"message": f"Subscribed to {plan} ({billing_cycle})"}), 201
