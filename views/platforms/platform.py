from flask import jsonify, request
from models import PostDraft


class PlatformView:

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
        return jsonify(message='Posted successfully.'), 201
