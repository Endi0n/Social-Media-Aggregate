from flask import session, redirect, request, jsonify
from .platform import PlatformView
from models.database import TumblrToken
from models.api import TumblrAPI
from app import db


class TumblrView(PlatformView):

    @staticmethod
    def auth():
        oauth_token, oauth_token_secret = TumblrAPI.generate_auth_req_token()

        session['tumblr_req_auth_token'], session['tumblr_req_auth_token_secret'] = oauth_token, oauth_token_secret

        return redirect(TumblrAPI.generate_auth_url(oauth_token))

    @staticmethod
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
