from models.api import TwitterAPI
from models.database import TwitterToken
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import login_required, twitter_required
from app import db

twitter = Blueprint(__name__, __name__, url_prefix='/twitter')


@twitter.route('/auth')
@login_required
def auth(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_req_token()
    session['twitter_req_auth_token'], session['twitter_req_auth_token_secret'] = oauth_token, oauth_token_secret
    return redirect(TwitterAPI.generate_auth_url(oauth_token))


@twitter.route('/auth/callback')
@login_required
def auth_callback(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_token(session['twitter_req_auth_token'],
                                                                     session['twitter_req_auth_token_secret'],
                                                                     request.args['oauth_verifier'])
    session.pop('twitter_req_auth_token')
    session.pop('twitter_req_auth_token_secret')

    token_record = TwitterToken(user, oauth_token, oauth_token_secret)
    db.session.add(token_record)
    db.session.commit()
    return jsonify({'message': 'Authentication succeeded.'}), 200


@twitter.route('/profile')
@twitter_required
def profile(twitter_client):
    return jsonify(twitter_client.get_profile())
