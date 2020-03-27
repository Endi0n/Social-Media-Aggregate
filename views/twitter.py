from models.api import TwitterAPI
from models.database import TwitterToken
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import login_required, twitter_required
from app import app, db

twitter = Blueprint(__name__, __name__, url_prefix='/twitter')


@twitter.route('/auth')
@login_required
def auth(user):
    session['request_token'], session['request_token_secret'] = TwitterAPI.generate_auth_req_token()
    return redirect(TwitterAPI.generate_auth_url(session['request_token']))


@twitter.route('/auth/callback')
@login_required
def auth_callback(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_token(session['request_token'],
                                                                     session['request_token_secret'],
                                                                     request.args['oauth_verifier'])
    session.pop('request_token', None)
    session.pop('request_token_secret', None)
    token_record = TwitterToken(user_id=user.id, token=oauth_token, token_secret=oauth_token_secret)
    db.session.add(token_record)
    db.session.commit()
    return jsonify({'message': 'Authentication succeeded.'}), 200


@twitter.route('/profile')
@twitter_required
def profile(twitter_client):
    return jsonify(twitter_client.get_profile())
