from requests_oauthlib import OAuth1Session
import pytumblr
import os
import json

class TumblrAPI:

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_base_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'
    callback_url = 'http://127.0.0.1:5000/tumblr/auth/callback'
    consumer_key = os.getenv('consumer_key')
    consumer_secret = os.getenv('consumer_secret') 

    fetch_response = None # temporary workaround

    @staticmethod
    def client(oauth_token, oauth_token_secret):
        return pytumblr.TumblrRestClient(
            TumblrAPI.consumer_key,
            TumblrAPI.consumer_secret,
            oauth_token,
            oauth_token_secret
        )

    @staticmethod
    def generate_auth_url(callback_url):
        oauth_session = OAuth1Session(
            TumblrAPI.consumer_key, 
            client_secret=TumblrAPI.consumer_secret, 
            callback_uri=callback_url
        )
        fetch_response = oauth_session.fetch_request_token(TumblrAPI.request_token_url)

        full_authorize_url = oauth_session.authorization_url(TumblrAPI.authorize_base_url)
        return full_authorize_url, fetch_response


    @staticmethod
    def generate_auth_token(redirect_uri, fetch_response):
        oauth_session = OAuth1Session(
            TumblrAPI.consumer_key, 
            client_secret=TumblrAPI.consumer_secret, 
            callback_uri=TumblrAPI.callback_url
        )

        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')

        # get verifier
        oauth_response = oauth_session.parse_authorization_response(redirect_uri)
        verifier = oauth_response.get('oauth_verifier')
        
        # Request final access token
        oauth_session = OAuth1Session(
            TumblrAPI.consumer_key,
            client_secret=TumblrAPI.consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier
        )
        return oauth_session.fetch_access_token(TumblrAPI.access_token_url)


if __name__ == '__main__':

    # /auth
    url, fetch_response = TumblrAPI.generate_auth_url('https://github.com/ceofil')
    
    # insert fetch_response.get('oauth_token') and fetch_response.get('oauth_token_secret')


    # /auth/callback
    red = input('go here {} and paste redirect: \n'.format(url))  #request.url

    # get fetch_response from data base

    access_token = TumblrAPI.generate_auth_token(red, fetch_response)

    client = TumblrAPI.client(access_token.get('oauth_token'), access_token.get('oauth_token_secret'))

    print(client.info())