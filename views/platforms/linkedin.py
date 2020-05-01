from flask import redirect, request, jsonify
from .platform import PlatformView
from models.database import LinkedInToken
from models.api import LinkedInAPI
from app import app, db
from datetime import datetime


class LinkedInView(PlatformView):
    CALLBACK_URL = app.config['BASE_DOMAIN'] + '/linkedin/auth/callback'

    @staticmethod
    def auth():
        return redirect(LinkedInAPI.generate_auth_url(LinkedInView.CALLBACK_URL))

    @staticmethod
    def auth_callback(user):
        token = LinkedInAPI.generate_auth_token(LinkedInView.CALLBACK_URL, request.url)
        token_record = LinkedInToken(user, token['access_token'],
                                     datetime.fromtimestamp(token['expires_at']))
        db.session.add(token_record)
        db.session.commit()

        return jsonify(message='Authentication succeeded.'), 200
