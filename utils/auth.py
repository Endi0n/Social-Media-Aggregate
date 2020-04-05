from functools import wraps
from flask import jsonify
from flask_login import current_user
from app import login_manager
from models.api import *
from models.database import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _verified_user_check(func):
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error='Unauthenticated.'), 401

        if not current_user.is_valid:
            return jsonify(error='Email is not validated.'), 403

        func(*args, **kwargs)

    return decorator


def verified_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error='Unauthenticated.'), 401

        if not current_user.is_valid:
            return jsonify(error='Email is not validated.'), 403

        return func(current_user, *args, **kwargs)

    return decorator


def linkedin_required(func):
    @wraps(func)
    @_verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.linkedin_token:
            return jsonify(error='Unauthenticated for LinkedIn.'), 401

        linkedin_client = LinkedInAPI(current_user.linkedin_token.token)
        return func(linkedin_client, *args, **kwargs)

    return decorator


def twitter_required(func):
    @wraps(func)
    @_verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.twitter_token:
            return jsonify(error='Unauthenticated for Twitter.'), 401

        twitter_client = TwitterAPI(current_user.twitter_token.token, current_user.twitter_token.token_secret)
        return func(twitter_client, *args, **kwargs)

    return decorator


def tumblr_required(func):
    @wraps(func)
    @_verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.tumblr_token:
            return jsonify(error='Unauthenticated for Tumblr.'), 401

        tumblr_client = TumblrAPI(current_user.tumblr_token.token, current_user.tumblr_token.token_secret)
        return func(tumblr_client, *args, **kwargs)

    return decorator
