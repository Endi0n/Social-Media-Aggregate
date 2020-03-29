from models.api import TumblrAPI
from models.database import TumblrToken
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import login_required, tumblr_required
from app import app, db

tumblr = Blueprint(__name__, __name__, url_prefix='/tumblr')
CALLBACK_URL = app.config['BASE_DOMAIN'] + '/tumblr/auth/callback'


@tumblr.route('/auth')
@login_required
def auth(user):
    oauth_token, oauth_token_secret = TumblrAPI.generate_auth_req_token()
    session['tumblr_req_auth_token'], session['tumblr_req_auth_token_secret'] = oauth_token, oauth_token_secret

    return redirect(TumblrAPI.generate_auth_url(oauth_token))


@tumblr.route('/auth/callback')
@login_required
def auth_callback(user):
    # temporary workound, this should be fetched from db

    oauth_token, oauth_token_secret = TumblrAPI.generate_auth_token(
        request.url,
        session['tumblr_req_auth_token'],
        session['tumblr_req_auth_token_secret']
    )

    session.pop('tumblr_req_auth_token')
    session.pop('tumblr_req_auth_token_secret')

    token_record = TumblrToken(user, oauth_token, oauth_token_secret)

    db.session.add(token_record)
    db.session.commit()

    return jsonify({'message': 'Authentication succeeded.'}), 200


@tumblr.route('/profile')
@tumblr_required
def profile(tumblr_client):
    return jsonify(tumblr_client.info())
