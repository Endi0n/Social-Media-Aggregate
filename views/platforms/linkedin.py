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
        access_token = token['access_token']
        access_token_exp = datetime.fromtimestamp(token['expires_at'])

        token_record = LinkedInToken.query.filter_by(user_id=user.id).first()

        if not token_record:
            token_record = LinkedInToken(user, access_token, access_token_exp)
            db.session.add(token_record)
        else:
            token_record.token, token_record.expires_at = access_token, access_token_exp

        db.session.commit()

        return jsonify(message='Authentication succeeded.'), 200

    @staticmethod
    def get_token_exp(user):
        return jsonify(exp=user.linkedin_token.expires_at.timestamp())
