from requests_oauthlib import OAuth2Session
from models import Profile, PostView, ImageEmbed
from models.database import Platform
from models.api.platform import PlatformAPI
from .error import LinkedInError
from datetime import date, datetime
import requests
import urllib
import json
import re


class LinkedInAPI(PlatformAPI):
    PLATFORM = Platform.query.filter_by(name='LINKEDIN').one()
    CLIENT_KEY = PLATFORM.client_key
    CLIENT_SECRET = PLATFORM.client_secret

    @staticmethod
    def generate_auth_url(callback_url):
        # Step 1
        authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, redirect_uri=callback_url,
                                 scope=['r_liteprofile', 'r_organization_social', 'w_organization_social',
                                        'rw_organization_admin'])

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
        self._client = OAuth2Session(LinkedInAPI.CLIENT_KEY, token={'access_token': token})

    def get_profile(self):
        profile = self._get_profile()
        followers = self._get_followers()

        post_id = profile['id']
        followers = followers['firstDegreeSize']
        name = f"{list(profile['firstName']['localized'].values())[0]} {list(profile['lastName']['localized'].values())[0]}"

        profile_picture = None
        if 'profilePicture' in profile:
            profile_picture = profile['profilePicture']['displayImage~']['elements'][-1]['identifiers'][0]['identifier']

        bio = profile.get('headline', None)

        profile.update({'followers': followers})

        return Profile(profile, post_id, followers, name=name, bio=bio, profile_picture=profile_picture).as_dict()

    def get_post(self, post_id):
        post = self._get_post(post_id)
        stats = self._get_post_stats(post_id)
        return self._get_post_view(post, stats)

    def get_posts(self):
        posts = {}

        current_week_no = date.today().isocalendar()[1]
        i = 0
        while True:
            for post in self._get_self_posts(0 + i, 20 + i)['elements']:
                if datetime.fromtimestamp(post['created']['time'] // 1e3).isocalendar()[1] != current_week_no:
                    return {'posts': list(posts.values())}
                posts[post['id']] = self._get_post_view(post, self._get_post_stats(post['id']))
                i += 1

    def post(self, post_draft):
        files = [self._upload_file(file) for file in post_draft.files]

        files_from_url = [requests.get(file) for file in post_draft.files_url]
        files.extend([self._upload_file(file_raw=file) for file in files_from_url])

        request_json = {
            'author': self._get_organization_urn(),
            'lifecycleState': 'PUBLISHED',

            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {'text': post_draft.text},
                    "shareMediaCategory": "NONE"
                }
            },

            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }

        if files:
            request_json['specificContent']['com.linkedin.ugc.ShareContent'].update({
                'shareMediaCategory': 'IMAGE',
                'media': [{'status': 'READY', 'media': file} for file in files]
            })

        json.loads(self._client.post(
            f'https://api.linkedin.com/v2/ugcPosts',
            json=request_json
        ).content.decode())

    def delete_post(self, post_id):
        self._client.delete('https://api.linkedin.com/v2/shares/' + post_id)

    def _get_profile(self):
        return json.loads(self._client.get(
            'https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture('
            'displayImage~digitalmediaAsset:playableStreams),headline)'
        ).content.decode())

    def _get_followers(self):
        companies = self._get_companies()['elements']
        if len(companies) < 1:
            raise LinkedInError(404, 'User has no company.')

        organization_urn = companies[0]['organizationalTarget']
        return json.loads(
            self._client.get(
                f'https://api.linkedin.com/v2/networkSizes/{organization_urn}?edgeType=CompanyFollowedByMember'
            ).content.decode())

    def _get_companies(self):
        return json.loads(
            self._client.get(
                'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR'
            ).content.decode())

    def _get_organization_urn(self):
        return self._get_companies()['elements'][0]['organizationalTarget']

    def _get_self_posts(self, start, count):
        # TODO:
        return json.loads(self._client.get(
            f'https://api.linkedin.com/v2/shares?q=owners&owners={self._get_organization_urn()}&sharesPerOwner=1000'
            f'&start={start}&count={count}'
        ).content.decode())

    def _get_self_posts2(self):
        self._client.headers.update({'X-Restli-Protocol-Version': '2.0.0'})

        organization_urn = self._get_companies()['elements'][0]['organizationalTarget']
        return json.loads(self._client.get(
            f'https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List({urllib.parse.quote(organization_urn)})'
        ).content.decode())

    def _get_post(self, post_id):
        return json.loads(self._client.get('https://api.linkedin.com/v2/shares/' + post_id).content.decode())

    def _get_post_stats(self, post_id):
        organization_urn = self._get_companies()['elements'][0]['organizationalTarget']

        return json.loads(self._client.get(
            'https://api.linkedin.com/v2/organizationalEntityShareStatistics?q=organizationalEntity'
            f'&organizationalEntity={organization_urn}&shares[0]=urn:li:share:{post_id}'
        ).content.decode())

    @staticmethod
    def _get_post_view(post, stats):
        post_id = id = post['id']
        timestamp = post['created']['time'] // 1e3

        likes = 0
        shares = 0
        comments_count = 0

        if stats['elements']:
            likes = stats['elements'][0]['totalShareStatistics']['likeCount']
            shares = stats['elements'][0]['totalShareStatistics']['commentCount']
            comments_count = stats['elements'][0]['totalShareStatistics']['commentCount']

        text = post['text']['text']
        hashtags = re.findall('#([^ .]+)', text)
        mentions = None  # TODO
        embeds = []

        if 'content' in post:
            for content in post['content']['contentEntities']:
                if 'entityLocation' in content:
                    embeds.append(ImageEmbed(content['entityLocation']))
                else:
                    pass

        return PostView(post, post_id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags,
                        embeds=embeds).as_dict()

    def _upload_file(self, file=None, file_raw=None):
        # Step 1
        data = json.loads(self._client.post(
            f'https://api.linkedin.com/v2/assets?action=registerUpload',
            json={
                "registerUploadRequest": {
                    "owner": self._get_organization_urn(),
                    "recipes": [
                        "urn:li:digitalmediaRecipe:feedshare-image"
                    ],
                    "serviceRelationships": [
                        {
                            "identifier": "urn:li:userGeneratedContent",
                            "relationshipType": "OWNER"
                        }
                    ],
                    "supportedUploadMechanism": [
                        "SYNCHRONOUS_UPLOAD"
                    ]
                }
            }
        ).content.decode())

        urn = data['value']['asset']
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'][
            'uploadUrl']

        # Step 2
        data = self._client.put(upload_url, headers={'Content-Type': 'image/jpeg,image/png,image/gif'},
                                data=file_raw or file.read())
        return urn
