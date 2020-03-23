from requests_oauthlib import OAuth1Session
from os import getenv


class TwitterAPI:
    CLIENT_KEY = getenv('TWITTER_API_KEY')
    CLIENT_SECRET = getenv('TWITTER_API_SECRET')

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

    def get_profile(self):
        oauth = OAuth1Session(self.CLIENT_KEY,
                              self.CLIENT_SECRET,
                              self.__oauth_token,
                              self.__oauth_token_secret)
        response = oauth.get('https://api.twitter.com/1.1/account/verify_credentials.json')
        return response.content.decode()
