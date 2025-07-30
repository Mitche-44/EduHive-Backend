# resources/admin/testimonial_admin.py

from flask import Blueprint, jsonify, request
from models.testimonial import Testimonial
from extensions import db

admin_testimonial_bp = Blueprint("admin_testimonial_bp", __name__, url_prefix="/api/admin/testimonials")


# Get all testimonials (including unapproved)
@admin_testimonial_bp.route("/", methods=["GET"])
def get_all_testimonials():
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    data = [
        {
            "id": t.id,
            "name": t.name,
            "role": t.role,
            "image": t.image,
            "rating": t.rating,
            "text": t.text,
            "is_approved": t.is_approved,
            "is_featured": t.is_featured,
            "created_at": t.created_at.isoformat(),
        }
        for t in testimonials
    ]
    return jsonify(data), 200


# Approve or reject a testimonial
@admin_testimonial_bp.route("/<int:testimonial_id>/moderate", methods=["PATCH"])
def moderate_testimonial(testimonial_id):
    data = request.get_json()
    testimonial = Testimonial.query.get_or_404(testimonial_id)

    testimonial.is_approved = data.get("is_approved", testimonial.is_approved)
    testimonial.is_featured = data.get("is_featured", testimonial.is_featured)

    db.session.commit()
    return jsonify({"message": "Testimonial updated."}), 200


# Delete a testimonial
@admin_testimonial_bp.route("/<int:testimonial_id>", methods=["DELETE"])
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    return jsonify({"message": "Testimonial deleted."}), 200
