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
        counter = dict()
        for note in notes:
            if note['type'] in counter:
                counter[note['type']] += 1
            else:
                counter[note['type']] = 1
        return counter


    def _get_post(self, post_id):
        username = self.info()['user']['name']
        blogname = '{}.tumblr.com'.format(username)
        response = self.posts(blogname, id=post_id, notes_info=True, filter='text')
        return response['posts'][0]


    def get_post(self, post_id):
        post = self._get_post(post_id)
        result = dict()

        result['id'] = post['id_string']
        result['created_at'] = post['timestamp']
        result['hashtags'] = post['tags']
        result['type'] = post['type']

        notes_info = self.get_notes_count_info(post['notes'])
        result['likes'] = notes_info['like']
        result['reblogs'] = notes_info['reblog']

        content = dict()
        if post['type'] == 'text':
            content['body'] = post['body']

        elif post['type'] == 'chat':
            content['body'] = post['body']

        elif post['type'] == 'link':
            content['link_image'] = post['link_image']
            content['url'] = post['url']
            content['excerpt'] = post['excerpt']
            content['description'] = post['description']

        elif post['type'] == 'photo':
            content['photos'] = post['photos']

        elif post['type'] == 'video':
            content['video_type'] = post['video_type']
            content['caption'] = post['caption']
            content['premalink_url'] = post['permalink_url']
            content['video'] = post['video']

        if 'title' in post:
            content['title'] = post['title']

        result['content'] = content
        return result

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
