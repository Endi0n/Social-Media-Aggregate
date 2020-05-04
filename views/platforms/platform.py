from flask import jsonify, request
from models import PostDraft
from models.database import FollowersCount, Stats
import utils.auth as auth
from app import db
from datetime import datetime


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

    @staticmethod
    def get_followers_stats(platform_cls):
        date_begin = datetime.fromtimestamp(request.args.get('date_begin', 0))

        date_end = None
        if 'date_end' in request.args:
            date_end = datetime.fromtimestamp(request.args['date_end'])
        else:
            date_end = datetime.utcnow()

        followers_count = FollowersCount.query.filter_by(
            user_id=auth.get_authenticated_user().id,
            platform_id=platform_cls.PLATFORM.id
        ).filter(FollowersCount.timestamp.between(date_begin, date_end)).order_by(FollowersCount.timestamp.desc()).all()

        return jsonify(followers_count=list(map(FollowersCount.as_dict, followers_count)))

    @staticmethod
    def get_general_stats(platform_cls):
        date_begin = datetime.fromtimestamp(request.args.get('date_begin', 0))

        date_end = None
        if 'date_end' in request.args:
            date_end = datetime.fromtimestamp(request.args['date_end'])
        else:
            date_end = datetime.utcnow()

        entries = Stats.query.filter_by(
            user_id=auth.get_authenticated_user().id,
            platform_id=platform_cls.PLATFORM.id
        ).filter(Stats.timestamp.between(date_begin, date_end)).order_by(Stats.timestamp.desc()).all()

        return jsonify(entries=list(map(Stats.as_dict, entries)))
