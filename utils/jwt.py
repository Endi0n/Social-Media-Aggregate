from app import app
from datetime import datetime
import jwt


def generate_validate_email_token(user):
    return jwt.encode({
        'iat': datetime.timestamp(datetime.utcnow()),
        'user_id': user.id,
        'email': user.email,
        'request_type': 'validate_email'
    }, app.config['SECRET_KEY']).decode()


def generate_reset_password_token(user):
    return jwt.encode({
        'iat': datetime.timestamp(datetime.utcnow()),
        'user_id': user.id,
        'email': user.email,
        'request_type': 'reset_password'
    }, app.config['SECRET_KEY']).decode()