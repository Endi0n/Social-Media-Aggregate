from app import app
from datetime import datetime
import jwt


def generate_validate_email_token(user):
    return jwt.encode(
        {'user_id': user.id, 'email': user.email, 'timestamp': datetime.timestamp(datetime.now())},
        app.config['SECRET_KEY']
    ).decode()
