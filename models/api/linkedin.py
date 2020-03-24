from requests_oauthlib import OAuth2Session
import os


class LinkedInAPI:
    CLIENT_KEY = os.getenv('LINKEDIN_API_KEY')
    CLIENT_SECRET = os.getenv('LINKEDIN_API_SECRET')
    CALLBACK_URL = 'https://auth.marecapitan.ro/'

    @staticmethod
    def generate_auth_url():
        # Step 1
        authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, redirect_uri=LinkedInAPI.CALLBACK_URL, scope=['r_liteprofile'])
        authorization_url, state = linkedin.authorization_url(authorization_base_url)
        return authorization_url

    @staticmethod
    def generate_auth_token(url):
        # Step 2
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, redirect_uri=LinkedInAPI.CALLBACK_URL)
        return linkedin.fetch_token('https://www.linkedin.com/oauth/v2/accessToken',
                                    client_secret=LinkedInAPI.CLIENT_SECRET,
                                    include_client_id=True,
                                    authorization_response=url)

    def __init__(self, token):
        self.__token = token

    def get_profile(self):
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, token={'access_token': self.__token})
        return linkedin.get('https://api.linkedin.com/v2/me').content.decode()


if __name__ == '__main__':
    print(LinkedInAPI.generate_auth_url())
    code = input("Paste the code: ")
    state = input("Paste the state: ")
    authorization_response = f'{LinkedInAPI.CALLBACK_URL}?code={code}&state={state}'
    token = LinkedInAPI.generate_auth_token(authorization_response)
    print(token)
    obj = LinkedInAPI(token['access_token'])
    print(obj.get_profile())





