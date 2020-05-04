from flask import jsonify, request
from models import PostDraft
from models.database import FollowersCount
import utils.auth as auth
from app import db


class PlatformView:
    __ROUTES__ = []

    @classmethod
    def route(cls, route, func):
        cls.__ROUTES__.append((route, func))
        return func

    @staticmethod
    def profile(client):
        return jsonify(client.get_profile())

    @staticmethod
    def post_endpoint(client, post_id):
        if request.method == 'GET':
            return jsonify(client.get_post(post_id))

        elif request.method == 'DELETE':
            client.delete_post(post_id)
            return jsonify(message='Post deleted.')

    @staticmethod
    def get_posts(client):
        return jsonify(client.get_posts())

    @staticmethod
    def post(client):
        client.post(PostDraft(request))
        followers_row = FollowersCount(auth.get_authenticated_user().id, client.PLATFORM.id,
                                       client.get_profile()['followers'], False)
        db.session.add(followers_row)
        db.session.commit()
        return jsonify(message='Posted successfully.'), 201

    @staticmethod
    def posts_stats(client):
        return jsonify(client.posts_stats())

    @staticmethod
    def get_posts_ranked(client):
        return jsonify(client.get_posts_ranked())
