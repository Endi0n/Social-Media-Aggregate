from models import TumblrAPI, TumblrToken, Post
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import verified_user_required, tumblr_required
from app import app, db

tumblr = Blueprint(__name__, __name__, url_prefix='/tumblr')
CALLBACK_URL = app.config['BASE_DOMAIN'] + '/tumblr/auth/callback'


@tumblr.route('/auth')
@verified_user_required
def auth(user):
    oauth_token, oauth_token_secret = TumblrAPI.generate_auth_req_token()
    session['tumblr_req_auth_token'], session['tumblr_req_auth_token_secret'] = oauth_token, oauth_token_secret

    return redirect(TumblrAPI.generate_auth_url(oauth_token))


@tumblr.route('/auth/callback')
@verified_user_required
def auth_callback(user):
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

    return jsonify(message='Authentication succeeded.'), 200


@tumblr.route('/profile')
@tumblr_required
def profile(tumblr_client):
    return jsonify(tumblr_client.info())



@tumblr.route('/post/<post_id>')
@tumblr_required
def view_post(tumblr_client, post_id):
    return jsonify(Post.from_tumblr(tumblr_client.get_post(post_id)).as_dict())

