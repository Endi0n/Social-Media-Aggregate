from functools import wraps
from flask import jsonify
from models.database import User
from models.api import *


def login_required(func):
    user = User.query.get(1)  # Temporary workaround

    @wraps(func)
    def decorator(*args, **kwargs):
        return func(user, *args, **kwargs)

    return decorator


def linkedin_required(func):
    user = User.query.get(1)  # Temporary workaround

    @wraps(func)
    def decorator(*args, **kwargs):
        if not user.linkedin_token:
            return jsonify({'error': 'Unauthenticated for LinkedIn.'}), 401

        linkedin_client = LinkedInAPI(user.linkedin_token.token)
        return func(linkedin_client, *args, **kwargs)

    return decorator
