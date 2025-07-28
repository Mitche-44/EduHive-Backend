
from flask_mail import Message
from extensions import mail
from flask import current_app

def send_email(subject, recipients, body):
    msg = Message(subject, recipients=recipients, body=body)
    mail.send(msg)

def send_subscriber_confirmation(email, name):
    body = f"Hi {name},\n\nThank you for subscribing to EduHive!"
    send_email("Welcome to EduHive!", [email], body)

def notify_admin_of_subscription(name, email, phone):
    admin_email = current_app.config.get("ADMIN_EMAIL")
    if admin_email:
        body = f"New subscriber:\n\nName: {name}\nEmail: {email}\nPhone: {phone}"
        send_email("New Newsletter Subscriber", [admin_email], body)
