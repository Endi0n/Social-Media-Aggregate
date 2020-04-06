from models.api import LinkedInAPI
from models.database import LinkedInToken
from flask import Blueprint, redirect, request, jsonify
from utils.auth import verified_user_required, linkedin_required
from app import app, db
from datetime import datetime

linkedin = Blueprint(__name__, __name__, url_prefix='/linkedin')
CALLBACK_URL = app.config['BASE_DOMAIN'] + '/linkedin/auth/callback'


@linkedin.route('/auth')
@verified_user_required
def auth(user):
    return redirect(LinkedInAPI.generate_auth_url(CALLBACK_URL))


@linkedin.route('/auth/callback')
@verified_user_required
def auth_callback(user):
    token = LinkedInAPI.generate_auth_token(CALLBACK_URL, request.url)
    token_record = LinkedInToken(user, token['access_token'],
                                 datetime.fromtimestamp(token['expires_at']))
    db.session.add(token_record)
    db.session.commit()
    return jsonify(message='Authentication succeeded.'), 200


@linkedin.route('/profile')
@linkedin_required
def profile(linkedin_client):
    profile = linkedin_client.get_profile()
    connections = linkedin_client.get_connections()

    res = {}
    res['name'] = f"{list(profile['firstName']['localized'].values())[0]} {list(profile['lastName']['localized'].values())[0]}"
    res['profile_picture'] = profile['profilePicture']['displayImage~']['elements'][-1]['identifiers'][0]['identifier']
    res['followers'] = connections

    return jsonify(res)


@linkedin.route('/profile/companies')
@linkedin_required
def get_companies(linkedin_client):
    return linkedin_client.get_companies()


@linkedin.route('/profile/posts')
@linkedin_required
def get_all_posts(linkedin_client):
    return linkedin_client.get_self_posts()


@linkedin.route('/post/<post_id>')
@linkedin_required
def view_post(linkedin_client, post_id):
    return jsonify(linkedin_client.get_post(post_id))
