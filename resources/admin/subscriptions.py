from flask import Blueprint, jsonify
from models.subscription import Subscription
from models.user import User
from extensions import db
from flask_jwt_extended import jwt_required
from decorators import admin_required

admin_subs_bp = Blueprint("admin_subs", __name__, url_prefix="/api/admin/subscriptions")

@admin_subs_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def get_subscriptions():
    subs = Subscription.query.join(User).add_columns(
        User.name, User.email, Subscription.plan,
        Subscription.billing_cycle, Subscription.subscribed_at,
        Subscription.expires_at, Subscription.is_active
    ).all()

    result = [
        {
            "user": {"name": name, "email": email},
            "plan": plan,
            "billing_cycle": billing,
            "subscribed_at": str(sub_at),
            "expires_at": str(exp_at),
            "is_active": active
        }
        for (_, name, email, plan, billing, sub_at, exp_at, active) in subs
    ]
    return jsonify(result)
