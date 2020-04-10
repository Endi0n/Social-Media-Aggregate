from models.api import TumblrAPI
from models.database import TumblrToken
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





# not consistent


def _get_post(client, post_id):
    username = client.info()['user']['name']
    blogname = '{}.tumblr.com'.format(username)
    response = client.posts(blogname, id=post_id)
    return response['posts'][0]




def get_post(client, post_id):
    post = _get_post(client, post_id)
    result = dict()
    
    result['id'] = post['id_string']
    result['created_at'] = post['timestamp']
    result['note_count'] = post['note_count']
    result['hashtags'] = post['tags']
    result['type'] = post['type']

    content = dict()
    if post['type'] == 'text':
        content['body'] = post['body']
        
    elif post['type'] == 'chat':
        content['body'] = post['body']

    elif post['type'] == 'link':
        content['link_image'] = post['link_image']
        content['url'] = post['url']
        content['excerpt'] = post['excerpt']
        content['description'] = post['description']

    elif post['type'] == 'photo':
        content['photos'] = post['photos']

    elif post['type'] == 'video':
        content['video_type'] = post['video_type']
        content['caption'] = post['caption']
        content['premalink_url'] = post['permalink_url']
        content['video'] = post['video']

    if 'title' in post:
        content['title'] = post['title']

    result['content'] = content
    return result
