from models.database import Platform
from models.post import *
from models import Profile, PostView, UserMention
from .platform import PlatformAPI
from requests_oauthlib import OAuth1Session
from datetime import datetime, date
from bs4 import BeautifulSoup
import requests
import re
import twitter


class TwitterAPI(PlatformAPI, twitter.Api):
    APP_KEY = Platform.query.filter_by(name='TWITTER').one()
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
        profile = self.VerifyCredentials().AsDict()

        profile_id = profile['screen_name']
        followers = profile.get('followers_count', 0)
        name = profile['name']
        bio = profile.get('description', None)

        profile_picture = None
        if 'profilePicture' in profile:
            profile_picture = profile['profilePicture']['displayImage~']['elements'][-1]['identifiers'][0]['identifier']

        return Profile(profile, profile_id, followers, name=name, bio=bio, profile_picture=profile_picture).as_dict()

    def get_post(self, post_id):
        return self._get_post_view(self.GetStatus(post_id).AsDict())

    def delete_post(self, post_id):
        self.DestroyStatus(post_id)

    def get_posts(self):
        posts = []
        max_id = None
        out_of_week = False
        user_id = self.VerifyCredentials().AsDict()['id']

        while not out_of_week:
            user_timeline_posts = [self._get_post_view(post.AsDict()) for post in
                                   self.GetUserTimeline(user_id, count=200, max_id=max_id)]
            if len(user_timeline_posts) == 0:
                break

            today_week_no = date.today().isocalendar()[1]

            for i in range(len(user_timeline_posts)):
                post = user_timeline_posts[i]
                post_date_time = datetime.fromtimestamp(post['created_at'])

                if today_week_no != post_date_time.isocalendar()[1]:
                    out_of_week = True
                    break

                posts.append(post)

            if len(posts) > 0:
                max_id = int(posts[-1]['id']) - 1

        return {'posts': posts}

    def post(self, post_draft):
        # Dirty fix because python-twitter is a dull library
        for file in post_draft.files:
            file.mode = 'rb'

        self.PostUpdate(status=post_draft.text, media=(post_draft.files + post_draft.files_url))

    @staticmethod
    def _get_post_view(post):
        post_id = post['id_str']
        timestamp = datetime.strptime(post['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
        likes = post.get('favorite_count', 0)
        shares = post.get('retweet_count', 0)

        screen_name = post['user']['screen_name']
        html = requests.get(f'https://twitter.com/{screen_name}/status/{post_id}')
        soup = BeautifulSoup(html.text, 'lxml')
        comments = soup.find_all('span', attrs={'class': 'ProfileTweet-actionCountForAria'})[0].contents[0].split()[0]
        comments_count = int(comments)

        text = post.get('full_text', '')
        urls = post['urls']
        for url in urls:
            text = text.replace(url['url'], url['expanded_url'])
        text = re.sub("https?://t.co/[a-zA-Z0-9]+$", '', text).strip()

        hashtags = [tag['text'] for tag in post['hashtags']]
        mentions = [UserMention(user['id'], name=user['name'], tag=user['screen_name'])
                    for user in post['user_mentions']]
        embeds = []

        if 'media' in post:
            for media in post['media']:
                if media['type'] == 'photo':
                    embeds.append(ImageEmbed(media['media_url_https']))

                elif media['type'] == 'video':
                    embeds.append(VideoEmbed(
                        max(media['video_info']['variants'],
                            key=lambda x: x['bitrate'] if 'bitrate' in x else -1)['url'],
                        cover_url=media['media_url_https'],
                        duration=media['video_info'].get('duration_millis', None)
                    ))

        if 'quoted_status' in post:
            embeds.append(QuoteEmbed(TwitterAPI._get_post_view(post['quoted_status'])))

        return PostView(post, post_id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags,
                        mentions=mentions, embeds=embeds).as_dict()

