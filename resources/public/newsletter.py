from flask import Blueprint, request, jsonify, send_file
from models.newsletter import NewsletterSubscriber
from extensions import db, mail
from flask_mail import Message
import csv, io, os, requests

newsletter_bp = Blueprint('newsletter', __name__, url_prefix="/api/newsletter")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_AUDIENCE_ID = os.getenv("MAILCHIMP_AUDIENCE_ID")

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    if not all([name, email, phone]):
        return jsonify({"error": "All fields are required"}), 400

    # Save subscriber
    subscriber = NewsletterSubscriber(name=name, email=email, phone=phone)
    db.session.add(subscriber)
    db.session.commit()

    # Send confirmation to subscriber
    msg = Message("EduHive Newsletter Confirmation",
                  recipients=[email],
                  body=f"Hi {name},\n\nThank you for subscribing to EduHive Newsletter!")
    mail.send(msg)

    # Notify admin
    admin_msg = Message("New Newsletter Subscriber",
                        recipients=[ADMIN_EMAIL],
                        body=f"New subscriber:\nName: {name}\nEmail: {email}\nPhone: {phone}")
    mail.send(admin_msg)

    # Add to Mailchimp
    mailchimp_url = f"https://usX.api.mailchimp.com/3.0/lists/{MAILCHIMP_AUDIENCE_ID}/members"
    response = requests.post(mailchimp_url,
        auth=("anystring", MAILCHIMP_API_KEY),
        json={
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {"FNAME": name}
        }
    )

    if response.status_code not in [200, 204]:
        print("Mailchimp error:", response.json())

    return jsonify({"message": "Subscription successful!"}), 201

@newsletter_bp.route('/export', methods=['GET'])
def export_subscribers():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Phone', 'Subscribed At'])

    for sub in NewsletterSubscriber.query.all():
        writer.writerow([sub.name, sub.email, sub.phone, sub.subscribed_at])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        download_name='subscribers.csv',
        as_attachment=True
    )
