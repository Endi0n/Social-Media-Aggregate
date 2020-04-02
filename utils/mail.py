from flask_mail import Message
from app import app, mail


def send_validate_email(email, token):
    msg = Message(
        'Validate your email for your Social Media Aggregate account!',
        body=f"Follow this link to activate your Social Media Aggregate account: {app.config['BASE_DOMAIN']}/auth/validate_email?token={token}",
        recipients=[email]
    )

    mail.send(msg)
