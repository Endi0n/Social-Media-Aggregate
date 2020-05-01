from flask import session, redirect, request, jsonify
from .platform import PlatformView
from models.database import TwitterToken
from models.api import TwitterAPI
from app import db


class TwitterView(PlatformView):

    @staticmethod
    def auth():
        oauth_token, oauth_token_secret = TwitterAPI.generate_auth_req_token()

        session['twitter_req_auth_token'], session['twitter_req_auth_token_secret'] = oauth_token, oauth_token_secret

        return redirect(TwitterAPI.generate_auth_url(oauth_token))

    @staticmethod
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
