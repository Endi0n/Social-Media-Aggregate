from flask import redirect, request, jsonify
from .platform import PlatformView
from models.database import LinkedInToken, DefaultPage
from models.api import LinkedInAPI
from utils.auth import current_user
import utils.request
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

    @staticmethod
    def default_page(client):
        if request.method == 'GET':
            default_page = DefaultPage.query.filter_by(user_id=current_user.id,
                                                       platform_id=client.PLATFORM.id).first()
            if default_page:
                default_page = default_page.page_id
            return jsonify(default_page=default_page)
        if request.method == 'POST' or request.method == 'PUT':
            new_default_page = utils.request.form_get('default_page')
            if new_default_page not in client.get_companies_id():
                return jsonify(error='Invalid company URN.'), 400

            default_page = DefaultPage.query.filter_by(user_id=current_user.id,
                                                       platform_id=client.PLATFORM.id).first()
            if default_page:
                default_page.page_id = new_default_page
            else:
                db.session.add(DefaultPage(current_user.id, client.PLATFORM.id, new_default_page))

            db.session.commit()
            return jsonify(message="Default page updated successfully.")
