from requests_oauthlib import OAuth2Session
from models.database import Platform
import requests
import urllib
import json


class LinkedInAPI:
    APP_KEY = Platform.query.filter_by(platform='LINKEDIN').one()
    CLIENT_KEY = APP_KEY.client_key
    CLIENT_SECRET = APP_KEY.client_secret

    application_token = None

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
        self.__linkedin = OAuth2Session(LinkedInAPI.CLIENT_KEY, token={'access_token': token})

    def get_profile(self):
        return json.loads(self.__linkedin.get(
            'https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture('
            'displayImage~digitalmediaAsset:playableStreams),headline)'
        ).content.decode())

    def get_followers(self):
        organization_urn = self.get_companies()['elements'][0]['organizationalTarget']
        return json.loads(
            self.__linkedin.get(
                f'https://api.linkedin.com/v2/networkSizes/{organization_urn}?edgeType=CompanyFollowedByMember'
            ).content.decode())

    def get_companies(self):
        return json.loads(
            self.__linkedin.get(
                'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR'
            ).content.decode())

    def get_self_posts(self, start, count):
        # TODO:
        return json.loads(self.__linkedin.get(
            f'https://api.linkedin.com/v2/shares?q=owners&owners={self.get_organization_urn()}&sharesPerOwner=1000'
            f'&start={start}&count={count}'
        ).content.decode())

    def get_self_posts2(self):
        self.__linkedin.headers.update({'X-Restli-Protocol-Version': '2.0.0'})

        organization_urn = self.get_companies()['elements'][0]['organizationalTarget']
        return json.loads(self.__linkedin.get(
            f'https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List({urllib.parse.quote(organization_urn)})'
        ).content.decode())

    def get_post(self, post_id):
        return json.loads(self.__linkedin.get('https://api.linkedin.com/v2/shares/' + post_id).content.decode())

    def get_post_stats(self, post_id):
        organization_urn = self.get_companies()['elements'][0]['organizationalTarget']

        return json.loads(self.__linkedin.get(
            'https://api.linkedin.com/v2/organizationalEntityShareStatistics?q=organizationalEntity'
            f'&organizationalEntity={organization_urn}&shares[0]=urn:li:share:{post_id}'
        ).content.decode())

    def get_organization_urn(self):
        return self.get_companies()['elements'][0]['organizationalTarget']

    def upload_file(self, file=None, file_raw=None):
        # Step 1
        data = json.loads(self.__linkedin.post(
            f'https://api.linkedin.com/v2/assets?action=registerUpload',
            json={
                "registerUploadRequest": {
                    "owner": self.get_organization_urn(),
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
        data = self.__linkedin.put(upload_url, headers={'Content-Type': 'image/jpeg,image/png,image/gif'},
                                   data=file_raw or file.read())
        return urn

    def post(self, post_draft):
        files = [self.upload_file(file) for file in post_draft.files]

        files_from_url = [requests.get(file) for file in post_draft.files_url]
        files.extend([self.upload_file(file_raw=file) for file in files_from_url])

        request_json = {
            'author': self.get_organization_urn(),
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

        json.loads(self.__linkedin.post(
            f'https://api.linkedin.com/v2/ugcPosts',
            json=request_json
        ).content.decode())


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
