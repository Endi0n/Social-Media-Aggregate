from requests_oauthlib import OAuth1Session
from models.database import AppKey
import json
from twitter import Api


class TwitterAPI:
    APP_KEY = AppKey.query.filter_by(platform='TWITTER').one()
    CLIENT_KEY = APP_KEY.client_key
    CLIENT_SECRET = APP_KEY.client_secret

    @staticmethod
    def generate_auth_req_token():
        # Step 1
        oauth_session = OAuth1Session(TwitterAPI.CLIENT_KEY, TwitterAPI.CLIENT_SECRET)
        tokens = oauth_session.fetch_request_token('https://api.twitter.com/oauth/request_token')
        return tokens['oauth_token'], tokens['oauth_token_secret']

    @staticmethod
    def generate_auth_url(oauth_token):
        # Step 2
        return 'https://api.twitter.com/oauth/authorize?oauth_token=' + oauth_token

    @staticmethod
    def generate_auth_token(request_token, request_token_secret, verifier):
        # Step 3
        oauth = OAuth1Session(TwitterAPI.CLIENT_KEY,
                              TwitterAPI.CLIENT_SECRET,
                              request_token,
                              request_token_secret,
                              verifier=verifier)

        tokens = oauth.fetch_access_token('https://api.twitter.com/oauth/access_token')
        return tokens['oauth_token'], tokens['oauth_token_secret']

    def __init__(self, auth_token, auth_token_secret):
        self.__oauth_token = auth_token
        self.__oauth_token_secret = auth_token_secret
        self.__api = Api(self.CLIENT_KEY,
                         self.CLIENT_SECRET,
                         self.__oauth_token,
                         self.__oauth_token_secret,
                         tweet_mode='extended')

    def get_profile(self):
        oauth = OAuth1Session(self.CLIENT_KEY,
                              self.CLIENT_SECRET,
                              self.__oauth_token,
                              self.__oauth_token_secret)
        response = oauth.get('https://api.twitter.com/1.1/account/verify_credentials.json')
        return json.loads(response.content.decode())

    def __post_json(self, status):
        post_json = {}
        if 'created_at' in status:
            post_json['utc-time'] = status['created_at']
        if 'hashtags' in status and len(status['hashtags']):
            post_json['hashtags'] = [tag['text'] for tag in status['hashtags']]
        if 'user_mentions' in status and len(status['user_mentions']):
            post_json['user_mentions'] = []
            for u in status['user_mentions']:
                post_json['user_mentions'].append({'screen_name': u['screen_name'],
                                                   'name': u['name'],
                                                   'id': u['id']})
        if 'retweet_count' in status:
            post_json['shares'] = status['retweet_count']
        if 'favorite_count' in status:
            post_json['likes'] = status['favorite_count']
        if 'full_text' in status:
            post_json['text'] = status['full_text']

        if 'media' in status:
            media = []
            for m in status['media']:
                media_dict = {'media_url': m['media_url_https'], 'type': m['type']}
                if 'video_info' in m:
                    media_dict['video_info'] = {}
                    media_dict['video_info']['aspect_ratio'] = m['video_info']['aspect_ratio']
                    media_dict['video_info']['duration_millis'] = m['video_info']['duration_millis']
                    media_dict['video_info']['url'] = max(m['video_info']['variants'],
                                                          key=lambda x: x['bitrate'] if 'bitrate' in x else -1)['url']
                media.append(media_dict)

            post_json['embed'] = media

        if 'quoted_status' in status:
            if 'embed' not in post_json:
                post_json['embed'] = []
            embed = self.__post_json(status['quoted_status'])
            embed['type'] = 'post'
            post_json['embed'].append(embed)

        return post_json

    def get_post(self, post_id):
        status = self.__api.GetStatus(post_id).AsDict()
        return self.__post_json(status)
