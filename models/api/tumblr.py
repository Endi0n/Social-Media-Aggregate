from models.database import Platform
from models import Profile, PostView, ImageEmbed, VideoEmbed
from .platform import PlatformAPI
from requests_oauthlib import OAuth1Session
from pytumblr import TumblrRestClient
import uuid
import os


class TumblrAPI(PlatformAPI, TumblrRestClient):
    APP_KEY = Platform.query.filter_by(name='TUMBLR').one()
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

    def get_profile(self):
        profile = self.info()

        profile_id = profile['user']['name']
        profile_picture = profile['user']['blogs'][0]['avatar'][0]['url']
        followers = profile['user']['blogs'][0]['followers']
        bio = profile['user']['blogs'][0]['description']

        return Profile(profile, profile_id, followers, bio=bio, profile_picture=profile_picture).as_dict()

    def get_post(self, post_id):
        return self._get_post_view(self._get_post(post_id))

    def delete_post(self, post_id):
        TumblrRestClient.delete_post(self, self._get_blogname(), post_id)

    def get_posts(self):
        profile = self.info()
        total_nr_of_posts = profile["user"]["blogs"][0]["posts"]

        response = self.posts(self._get_blogname(), notes_info=True, limit=total_nr_of_posts)
        unfiltered_posts = response['posts']

        posts = []
        for post in unfiltered_posts:
            posts.append(self._get_post_view(post))

        return {'posts': posts}

    @staticmethod
    def _get_post_view(post):
        post_id = post['id_string']
        timestamp = post['timestamp']
        hashtags = post['tags']
        likes = 0
        shares = 0
        comments_count = 0
        text = None
        embeds = []

        if 'notes' in post:
            for note in post['notes']:
                if note['type'] == 'like':
                    likes += 1
                elif note['type'] == 'reblog':
                    shares += 1
                elif note['type'] == 'reply':
                    comments_count += 1

        if post['type'] == 'text':
            text = post['body']
        elif post['type'] == 'chat':
            text = post['body']
        elif post['type'] == 'link':
            text = post['url']
            # post['link_image']
            # post['url']
            # post['excerpt']
            # post['description']
        elif post['type'] == 'photo':
            for photo in post['photos']:
                embeds.append(ImageEmbed(photo['original_size']['url']))
        elif post['type'] == 'video':
            embeds.append(VideoEmbed(post['permalink_url'], cover_url=post['thumbnail_url']))

        return PostView(post, post_id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags,
                        embeds=embeds).as_dict()

    def _get_post(self, post_id):
        response = self.posts(self._get_blogname(), id=post_id, notes_info=True)
        return response['posts'][0]

    def _get_blogname(self):
        username = self.info()['user']['name']
        blogname = '{}.tumblr.com'.format(username)
        return blogname

    def post(self, post_draft):
        blogName = self._get_blogname()

        if post_draft.files:
            files = dict()
            for file in post_draft.files:
                file_type = file.headers['Content-Type'].split('/')[0]
                if file_type not in files:
                    files[file_type] = []
                temp_dir = '/tmp'
                temp_name = "{}_{}".format(str(uuid.uuid1()), file.filename)
                filepath = os.path.join(temp_dir, temp_name)
                file.save(filepath)

                print(filepath, file_type)

                files[file_type].append(filepath)

            if 'image' in files:
                result = self.create_photo(blogName, data=files['image'], caption=post_draft.text)
            elif 'video' in files:
                result = self.create_video(blogName, data=files['video'], caption=post_draft.text)

            for _type in files:
                for filepath in files[_type]:
                    os.remove(filepath)

        elif post_draft.files_url:
            urls = dict()
            for url in post_draft.files_url:
                file_type = 'photo'  # TODO  get file type from url

                if file_type not in urls:
                    urls[file_type] = []
                urls[file_type].append(url)

            if 'photo' in urls:
                result = self.create_photo(blogName, source=urls['photo'][0], caption=post_draft.text)
            elif 'video' in urls:
                result = self.create_video(blogName, embed=urls['video'][0], caption=post_draft.text)

        # TODO  check result
