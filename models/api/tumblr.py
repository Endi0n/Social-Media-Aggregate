from models.database import AppKey
from requests_oauthlib import OAuth1Session
from pytumblr import TumblrRestClient


class TumblrAPI(TumblrRestClient):
    APP_KEY = AppKey.query.filter_by(platform='TUMBLR').one()
    CLIENT_KEY = APP_KEY.client_key
    CLIENT_SECRET = APP_KEY.client_secret

    REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
    AUTHORIZE_BASE_URL = 'https://www.tumblr.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'

    def __init__(self, oauth_token, oauth_token_secret):
        TumblrRestClient.__init__(
            self,
            TumblrAPI.CLIENT_KEY,
            TumblrAPI.CLIENT_SECRET,
            oauth_token,
            oauth_token_secret
        )

    @staticmethod
    def generate_auth_req_token():
        oauth_session = OAuth1Session(
            TumblrAPI.CLIENT_KEY,
            client_secret=TumblrAPI.CLIENT_SECRET
        )

        tokens = oauth_session.fetch_request_token(TumblrAPI.REQUEST_TOKEN_URL)
        return tokens['oauth_token'], tokens['oauth_token_secret']

    @staticmethod
    def generate_auth_url(oauth_token):
        return f'{TumblrAPI.AUTHORIZE_BASE_URL}?oauth_token={oauth_token}'

    @staticmethod
    def generate_auth_token(url, oauth_token, oauth_secret):
        oauth_session = OAuth1Session(
            TumblrAPI.CLIENT_KEY,
            client_secret=TumblrAPI.CLIENT_SECRET,
            callback_uri=url
        )

        # get verifier
        oauth_response = oauth_session.parse_authorization_response(url)
        verifier = oauth_response.get('oauth_verifier')
        
        # Request final access token
        oauth_session = OAuth1Session(
            TumblrAPI.CLIENT_KEY,
            client_secret=TumblrAPI.CLIENT_SECRET,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret,
            verifier=verifier
        )

        tokens = oauth_session.fetch_access_token(TumblrAPI.ACCESS_TOKEN_URL)
        return tokens['oauth_token'], tokens['oauth_token_secret']

    def get_notes_count_info(self, notes):
        counter = {
            'like': 0,
            'reblog': 0
        }
        for note in notes:
            if note['type'] in counter:
                counter[note['type']] += 1
            else:
                counter[note['type']] = 1
        return counter

    def _get_post(self, post_id):
        username = self.info()['user']['name']
        blogname = '{}.tumblr.com'.format(username)
        response = self.posts(blogname, id=post_id, notes_info=True)
        return response['posts'][0]
    
    def _get_blogname(self):
        username = self.info()['user']['name']
        blogname = '{}.tumblr.com'.format(username)
        return blogname

