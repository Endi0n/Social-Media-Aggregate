from functools import wraps
from flask import jsonify, request, session, redirect
from flask_login import current_user
from app import login_manager
from models.api import *
from models.database import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_authenticated_user():
    if not current_user.is_authenticated:
        return None
    return current_user


def verified_user_check(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error='Unauthenticated.'), 401

        if not current_user.is_active:
            return jsonify(error='Email is not validated.'), 403

        return func(*args, **kwargs)

    return decorator


def verified_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error='Unauthenticated.'), 401

        if not current_user.is_active:
            return jsonify(error='Email is not validated.'), 403

        return func(current_user, *args, **kwargs)

    return decorator


def linkedin_required(func):
    @wraps(func)
    @verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.linkedin_token:
            return jsonify(error='Unauthenticated for LinkedIn.'), 401

        linkedin_client = LinkedInAPI(current_user.linkedin_token.token)
        return func(linkedin_client, *args, **kwargs)

    return decorator


def twitter_required(func):
    @wraps(func)
    @verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.twitter_token:
            return jsonify(error='Unauthenticated for Twitter.'), 401

        twitter_client = TwitterAPI(current_user.twitter_token.token, current_user.twitter_token.token_secret)
        return func(twitter_client, *args, **kwargs)

    return decorator


def tumblr_required(func):
    @wraps(func)
    @verified_user_check
    def decorator(*args, **kwargs):
        if not current_user.tumblr_token:
            return jsonify(error='Unauthenticated for Tumblr.'), 401

        tumblr_client = TumblrAPI(current_user.tumblr_token.token, current_user.tumblr_token.token_secret)
        return func(tumblr_client, *args, **kwargs)

    return decorator


def platform_auth(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        redirect_url = request.args.get('redirect_url', None)
        if redirect_url:
            session['redirect_url'] = redirect_url
        return func(*args, **kwargs)

    return verified_user_check(decorator)


def platform_callback(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        res = func(*args, **kwargs)

        if 'redirect_url' in session:
            redirect_url = session['redirect_url']
            session.pop('redirect_url')
            return redirect(redirect_url)

        return res

    return verified_user_required(decorator)
