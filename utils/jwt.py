from app import app
from datetime import datetime
import jwt


def encode(data):
    data = data.copy()
    data.update({'iat': datetime.timestamp(datetime.utcnow())})

    return jwt.encode(data, app.config['SECRET_KEY']).decode()


def generate_validate_email_token(user):
    return encode({
        'user_id': user.id,
        'email': user.email,
        'request_type': 'validate_email'
    })


def generate_reset_password_token(user):
    return encode({
        'user_id': user.id,
        'email': user.email,
        'request_type': 'reset_password'
    })


def generate_token(user):
    return encode({
        'user_id': user.id,
    })
