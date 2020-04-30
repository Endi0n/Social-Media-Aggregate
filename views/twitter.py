from models import TwitterAPI, TwitterToken, PostView, Profile, PostDraft
from flask import Blueprint, redirect, request, jsonify, session
from utils.auth import verified_user_required, twitter_required
from app import db

twitter = Blueprint(__name__, __name__, url_prefix='/twitter')


@twitter.route('/auth')
@verified_user_required
def auth(user):
    oauth_token, oauth_token_secret = TwitterAPI.generate_auth_req_token()

    session['twitter_req_auth_token'], session['twitter_req_auth_token_secret'] = oauth_token, oauth_token_secret

    redirect_url = request.args.get('redirect_url', None)
    if redirect_url:
        session['redirect_url'] = redirect_url

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

    if 'redirect_url' in session:
        redirect_url = session['redirect_url']
        session.pop('redirect_url')
        return redirect(redirect_url)

    return jsonify(message='Authentication succeeded.'), 200


@twitter.route('/profile')
@twitter_required
def profile(twitter_client):
    return jsonify(Profile.from_twitter(twitter_client.VerifyCredentials().AsDict()).as_dict())


@twitter.route('/post/<post_id>')
@twitter_required
def view_post(twitter_client, post_id):
    return jsonify(PostView.from_twitter(twitter_client.GetStatus(post_id).AsDict()).as_dict())


@twitter.route('/profile/posts')
@twitter_required
def get_user_posts(twitter_client):
    posts = {'posts': []}
    max_id = int(request.args['last_id'])-1 if 'last_id' in request.args else None
    count = request.args.get('count', 5)
    user_id = twitter_client.VerifyCredentials().AsDict()['id']

    user_timeline = twitter_client.GetUserTimeline(user_id, count=count, max_id=max_id)
    posts['posts'] = [PostView.from_twitter(post.AsDict()).as_dict() for post in user_timeline]

    return jsonify(posts)


@twitter.route('/post', methods=['POST'])
@twitter_required
def post(twitter_client):
    twitter_client.post(PostDraft(request))
    return jsonify(message='Posted successfully.'), 201
