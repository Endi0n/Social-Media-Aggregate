from models import TwitterAPI, TwitterToken, Post, Profile
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import verified_user_required, twitter_required
from app import db

twitter = Blueprint(__name__, __name__, url_prefix='/twitter')


@twitter.route('/auth')
@verified_user_required
def auth(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_req_token()
    session['twitter_req_auth_token'], session['twitter_req_auth_token_secret'] = oauth_token, oauth_token_secret
    return redirect(TwitterAPI.generate_auth_url(oauth_token))


@twitter.route('/auth/callback')
@verified_user_required
def auth_callback(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_token(session['twitter_req_auth_token'],
                                                                     session['twitter_req_auth_token_secret'],
                                                                     request.args['oauth_verifier'])
    session.pop('twitter_req_auth_token')
    session.pop('twitter_req_auth_token_secret')

    token_record = TwitterToken(user, oauth_token, oauth_token_secret)
    db.session.add(token_record)
    db.session.commit()
    return jsonify(message='Authentication succeeded.'), 200


@twitter.route('/profile')
@twitter_required
def profile(twitter_client):
    return jsonify(Profile.from_twitter(twitter_client.VerifyCredentials().AsDict()).as_dict())


@twitter.route('/post/<post_id>')
@twitter_required
def view_post(twitter_client, post_id):
    return jsonify(Post.from_twitter(twitter_client.GetStatus(post_id).AsDict()).as_dict())
