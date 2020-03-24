from requests_oauthlib import OAuth1Session
import pytumblr
import os
import json


class TumblrAPI:

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = None
        self.oauth_token_secret = None
        self.client = None

    def init_client(self):
        self.client = pytumblr.TumblrRestClient(
            self.consumer_key,
            self.consumer_secret,
            self.oauth_token,
            self.oauth_token_secret
        )

    def authorize(self):
        # Obtain request token
        oauth_session = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret)
        fetch_response = oauth_session.fetch_request_token(self.request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')

        # Authorize URL + Response
        full_authorize_url = oauth_session.authorization_url(self.authorize_url)

        # Redirect to authentication page
        print('\nPlease go here and authorize:\n{}'.format(full_authorize_url))
        redirect_response = input('Allow then paste the full redirect URL here:\n').strip()
        assert redirect_response

        # Retrieve oauth verifier
        oauth_response = oauth_session.parse_authorization_response(redirect_response)
        verifier = oauth_response.get('oauth_verifier')

        # Request final access token
        oauth_session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier
        )
        oauth_tokens = oauth_session.fetch_access_token(self.access_token_url)

        self.oauth_token = oauth_tokens.get('oauth_token')
        self.oauth_token_secret = oauth_tokens.get('oauth_token_secret')

    def cache_tokens(self, path):
        with open(path, 'w') as cache:
            tokens = {
                'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'oauth_token': self.oauth_token,
                'oauth_token_secret': self.oauth_token_secret
            }
            json.dump(tokens, cache, indent=4)

    def load_cache(self, path):
        with open(path, 'r') as cache:
            tokens = json.load(cache)
            self.consumer_key = tokens['consumer_key']
            self.consumer_secret = tokens['consumer_secret']
            self.oauth_token = tokens['oauth_token']
            self.oauth_token_secret = tokens['oauth_token_secret']


def _dev_cache():
    cache_path = 'cache.json'
    demo = TumblrAPI(consumer_key, consumer_secret)

    if os.path.exists(cache_path):
        demo.load_cache(cache_path)
        demo.init_client()

        if 'user' not in demo.client.info():
            demo.client = None  # invalid cache

    # if there is no cache or the cache is invalid
    if demo.client is None:
        demo.authorize()
        demo.init_client()
        demo.cache_tokens(cache_path)
    return demo


if __name__ == '__main__':

    os.chdir(r'C:\Users\Teo\PycharmProjectst')

    with open('data.json', 'r') as data:
        data_json = json.load(data)
        consumer_key = data_json['consumer_key']
        consumer_secret = data_json['consumer_secret']

    _dev_mode = False

    if _dev_mode:
        # made this so I don't have to allow and paste the redirect every time I run the code
        # it will be removed from the final version
        demo = _dev_cache()
    else:
        demo = TumblrAPI(consumer_key, consumer_secret)
        demo.authorize()
        demo.init_client()

    # Hello world
    print(json.dumps(demo.client.info(), indent=4))
