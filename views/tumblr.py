from models.api import TumblrAPI
from models.database import TumblrToken
from flask import Blueprint, redirect, request, jsonify
from utils.auth import login_required, tumblr_required
from app import app, db
from datetime import datetime
from models.database import User
import json


tumblr = Blueprint(__name__, __name__, url_prefix='/tumblr')
CALLBACK_URL = app.config['BASE_DOMAIN'] + '/tumblr/auth/callback'


@tumblr.route('/auth')
@login_required
def auth(user):
    redirect_url, fetch_response = TumblrAPI.generate_auth_url(CALLBACK_URL)

    # temporary workound, this should be inserted into db
    TumblrAPI.fetch_response = fetch_response 

    return redirect(redirect_url)


@tumblr.route('/auth/callback')
@login_required
def auth_callback(user):
    # temporary workound, this should be fetched from db
    fetch_response = TumblrAPI.fetch_response
    
    access_token = TumblrAPI.generate_auth_token(request.url, fetch_response)

    token_record = TumblrToken(
        None, 
        access_token.get('oauth_token'), 
        access_token.get('oauth_token_secret')
    )

    db.session.add(token_record)
    db.session.commit()

    return jsonify({'message': 'Authentication succeeded.'}), 200


@tumblr.route('/profile')
@tumblr_required
def profile(tumblr_client):
    return jsonify(tumblr_client.info())
