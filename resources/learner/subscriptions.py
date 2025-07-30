# from flask import Blueprint, request, jsonify
# from extensions import db
# from models.subscription import Subscription
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from datetime import datetime, timedelta

# subscription_bp = Blueprint("subscription", __name__, url_prefix="/api/subscription")

# @subscription_bp.route("/subscribe", methods=["POST"])
# @jwt_required()
# def subscribe():
#     data = request.get_json()
#     plan = data.get("plan")
#     billing_cycle = data.get("billing_cycle")

#     if plan not in ["Free", "Basic", "Pro", "Elite"]:
#         return jsonify({"error": "Invalid plan"}), 400

#     if billing_cycle not in ["monthly", "yearly"]:
#         return jsonify({"error": "Invalid billing cycle"}), 400

#     user_id = get_jwt_identity()

#     # Calculate end date
#     duration = timedelta(days=365 if billing_cycle == "yearly" else 30)
#     end_date = datetime.utcnow() + duration

#     # Check if already subscribed
#     existing = Subscription.query.filter_by(user_id=user_id, active=True).first()
#     if existing:
#         existing.active = False
#         db.session.commit()

#     subscription = Subscription(
#         user_id=user_id,
#         plan=plan,
#         billing_cycle=billing_cycle,
#         start_date=datetime.utcnow(),
#         end_date=end_date,
#         active=True
#     )
#     db.session.add(subscription)
#     db.session.commit()

#     return jsonify({"message": f"Subscribed to {plan} ({billing_cycle})"}), 201



from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Subscription, BillingHistory
from datetime import datetime, timedelta
from app import socketio

subscriptions_bp = Blueprint("subscriptions", __name__)

@subscriptions_bp.route("/api/user/subscription/upgrade", methods=["POST"])
@jwt_required()
def upgrade_subscription():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_plan = data.get("plan")

    if not new_plan:
        return jsonify({"error": "Plan is required"}), 400

    # Fetch current subscription
    subscription = Subscription.query.filter_by(user_id=user_id, active=True).first()
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404

    # Avoid redundant upgrades
    if subscription.plan == new_plan:
        return jsonify({"error": "You're already on this plan"}), 400

    billing_cycle = subscription.billing_cycle or "monthly"  # fallback if null
    plan_prices = {
        "Free": 0,
        "Basic": 20,
        "Pro": 50,
        "Elite": 100,
    }
    amount = plan_prices.get(new_plan)
    if amount is None:
        return jsonify({"error": "Invalid plan selected"}), 400

    # Deactivate current subscription and create a new one
    subscription.active = False
    db.session.commit()

    # New subscription
    duration = timedelta(days=365 if billing_cycle == "yearly" else 30)
    new_subscription = Subscription(
        user_id=user_id,
        plan=new_plan,
        billing_cycle=billing_cycle,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + duration,
        renewal_date=datetime.utcnow() + duration,
        active=True
    )
    db.session.add(new_subscription)
    db.session.commit()

    # Emit WebSocket event to admins
    socketio.emit("subscription_updated", {
        "user_id": user_id,
        "plan": new_plan,
        "billing_cycle": billing_cycle
    }, namespace="/admin")

    # Log billing
    history = BillingHistory(
        user_id=user_id,
        plan=new_plan,
        billing_cycle=billing_cycle,
        amount=f"${amount:.2f}",
        created_at=datetime.utcnow(),
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Upgraded to {new_plan} ({billing_cycle})",
        "plan": new_plan,
        "billing_cycle": billing_cycle,
        "renewal_date": new_subscription.renewal_date.isoformat()
    }), 200

