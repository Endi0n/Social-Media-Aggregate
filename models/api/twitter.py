from requests_oauthlib import OAuth1Session
from models.database import AppKey
import twitter


class TwitterAPI(twitter.Api):
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

    def __init__(self, oauth_token, oauth_token_secret):
        twitter.Api.__init__(self, self.CLIENT_KEY,
                             self.CLIENT_SECRET,
                             oauth_token,
                             oauth_token_secret,
                             tweet_mode='extended')

    def get_profile(self):
        profilestatus = self.VerifyCredentials().AsDict()
        profile_json = {}
        if 'name' in profilestatus:
            profile_json['user_name'] = profilestatus['name']
        if 'followers_count' in profilestatus:
            profile_json['followers'] = profilestatus['followers_count']
        if 'screen_name' in profilestatus:
            profile_json['follow_name'] = profilestatus['screen_name']
        if 'profile_image_url_https' in profilestatus:
            profile_json['profile_image'] = profilestatus['profile_image_url_https']
        return profile_json
