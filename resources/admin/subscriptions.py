# from flask import Blueprint, jsonify
# from models.subscription import Subscription
# from models.user import User
# from extensions import db
# from flask_jwt_extended import jwt_required
# from decorators import admin_required

# admin_subs_bp = Blueprint("admin_subs", __name__, url_prefix="/api/admin/subscriptions")

# @admin_subs_bp.route("/", methods=["GET"])
# @jwt_required()
# @admin_required
# def get_subscriptions():
#     subs = Subscription.query.join(User).add_columns(
#         User.name, User.email, Subscription.plan,
#         Subscription.billing_cycle, Subscription.subscribed_at,
#         Subscription.expires_at, Subscription.is_active
#     ).all()

#     result = [
#         {
#             "user": {"name": name, "email": email},
#             "plan": plan,
#             "billing_cycle": billing,
#             "subscribed_at": str(sub_at),
#             "expires_at": str(exp_at),
#             "is_active": active
#         }
#         for (_, name, email, plan, billing, sub_at, exp_at, active) in subs
#     ]
#     return jsonify(result)


from flask import Blueprint, jsonify
from models import db, Subscription, User
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from extensions import db

admin_subscriptions_bp = Blueprint("admin_subscriptions", __name__)

@admin_subscriptions_bp.route("/api/admin/subscriptions", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all_subscriptions():
    subs = (
        db.session.query(Subscription, User)
        .join(User, Subscription.user_id == User.id)
        .all()
    )

    data = [
        {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "plan": sub.plan,
            "status": sub.status,
            "billing_cycle": sub.billing_cycle,
            "renewal_date": sub.renewal_date.isoformat(),
            "created_at": sub.created_at.isoformat(),
        }
        for sub, user in subs
    ]

    return jsonify({"subscriptions": data}), 200

