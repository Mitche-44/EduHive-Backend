# resources/public/testimonial.py

from flask import Blueprint, jsonify, request
from models.testimonial import Testimonial
from extensions import db

testimonial_bp = Blueprint("testimonial_bp", __name__, url_prefix="/api/testimonials")


@testimonial_bp.route("/", methods=["GET"])
def get_testimonials():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = Testimonial.query.order_by(Testimonial.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    testimonials = pagination.items

    data = [
        {
            "id": t.id,
            "name": t.name,
            "role": t.role,
            "image": t.image,
            "rating": t.rating,
            "text": t.text,
            "created_at": t.created_at.isoformat(),
        }
        for t in testimonials
    ]

    return jsonify({
        "testimonials": data,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages
    }), 200


@testimonial_bp.route("/", methods=["POST"])
def create_testimonial():
    data = request.get_json()

    required_fields = ["name", "role", "rating", "text"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    testimonial = Testimonial(
        name=data["name"],
        role=data["role"],
        image=data.get("image"),
        rating=int(data["rating"]),
        text=data["text"],
    )
    db.session.add(testimonial)
    db.session.commit()

    return jsonify({"message": "Testimonial submitted successfully."}), 201
