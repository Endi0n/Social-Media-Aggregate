from requests_oauthlib import OAuth2Session
from models.database import AppKey
import json


class LinkedInAPI:
    APP_KEY = AppKey.query.filter_by(platform='LINKEDIN').one()
    CLIENT_KEY = APP_KEY.client_key
    CLIENT_SECRET = APP_KEY.client_secret

    @staticmethod
    def generate_auth_url(callback_url):
        # Step 1
        authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, redirect_uri=callback_url, scope=['r_liteprofile'])
        authorization_url, state = linkedin.authorization_url(authorization_base_url)
        return authorization_url

    @staticmethod
    def generate_auth_token(callback_url, url):
        # Step 2
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, redirect_uri=callback_url)
        return linkedin.fetch_token('https://www.linkedin.com/oauth/v2/accessToken',
                                    client_secret=LinkedInAPI.CLIENT_SECRET,
                                    include_client_id=True,
                                    authorization_response=url)

    def __init__(self, token):
        self.__linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, token={'access_token': token})
        self.__user_id = self.get_profile()['id']

    def get_profile(self):
        return json.loads(self.__linkedin.get('https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture(displayImage~digitalmediaAsset:playableStreams))').content.decode())

    def get_connections(self):
        return json.loads(self.__linkedin.get('https://api.linkedin.com/v2/connections?q=viewer&count=0').content.decode())

if __name__ == '__main__':
    import os

    callback_url = os.getenv('BASE_DOMAIN')
    print(LinkedInAPI.generate_auth_url(callback_url))
    code = input('Paste the code: ')
    state = input('Paste the state: ')
    authorization_response = f'{callback_url}?code={code}&state={state}'
    token = LinkedInAPI.generate_auth_token(callback_url, authorization_response)
    print(token)
    obj = LinkedInAPI(token['access_token'])
    print(obj.get_profile())
