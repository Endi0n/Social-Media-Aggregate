from functools import wraps
from flask import jsonify
from models.database import User
from models.api import *


def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = User.query.get(1)  # Temporary workaround

        return func(user, *args, **kwargs)

    return decorator


def linkedin_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = User.query.get(1)  # Temporary workaround

        if not user.linkedin_token:
            return jsonify({'error': 'Unauthenticated for LinkedIn.'}), 401

        linkedin_client = LinkedInAPI(user.linkedin_token.token)
        return func(linkedin_client, *args, **kwargs)

    return decorator


def twitter_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = User.query.get(1)  # Temporary workaround

        if not user.twitter_token:
            return jsonify({'error': 'Unauthenticated for Twitter.'}), 401

        twitter_client = TwitterAPI(user.twitter_token.token, user.twitter_token.token_secret)
        return func(twitter_client, *args, **kwargs)

    return decorator


def tumblr_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = User.query.get(1)  # Temporary workaround

        if not user.tumblr_token:
            return jsonify({'error': 'Unauthenticated for Tumblr.'}), 401

        tumblr_client = TumblrAPI(user.tumblr_token.token, user.tumblr_token.token_secret)
        return func(tumblr_client, *args, **kwargs)

    return decorator
