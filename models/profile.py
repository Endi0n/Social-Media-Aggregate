import os


class Profile:

    def __init__(self, id, followers, name=None, bio=None, profile_picture=None, original=None):
        self.__id = id
        self.__followers = followers
        self.__name = name
        self.__bio = bio
        self.__profile_picture = profile_picture

        self.__original = original

    def as_dict(self):
        profile = {
            'id': self.__id,
            'followers': self.__followers,
        }

        if self.__name:
            profile['name'] = self.__name

        if self.__bio:
            profile['bio'] = self.__bio

        if self.__profile_picture:
            profile['profile_picture'] = self.__profile_picture

        if self.__original and os.getenv('DEBUG_PROFILE'):
            profile['original'] = self.__original

        return profile

    @classmethod
    def from_linkedin(cls, profile, followers):
        id = profile['id']
        followers = followers['firstDegreeSize']
        name = f"{list(profile['firstName']['localized'].values())[0]} {list(profile['lastName']['localized'].values())[0]}"
        profile_picture = None
        if 'profilePicture' in profile:
            profile_picture = profile['profilePicture']['displayImage~']['elements'][-1]['identifiers'][0]['identifier']
        bio = profile.get('headline', None)
        profile.update({'followers': followers})

        return cls(id, followers, name=name, bio=bio, profile_picture=profile_picture, original=profile)

    @classmethod
    def from_twitter(cls, profile):
        id = profile['screen_name']
        followers = profile.get('followers_count', None)
        name = profile['name']
        profile_picture = None
        if 'profilePicture' in profile:
            profile_picture = profile['profilePicture']['displayImage~']['elements'][-1]['identifiers'][0]['identifier']
        bio = profile.get('description', None)

        return cls(id, followers, name=name, bio=bio, profile_picture=profile_picture, original=profile)

    @classmethod
    def from_tumblr(cls, profile):
        id = profile['user']['name']
        profile_picture = profile['user']['blogs'][0]['avatar'][0]['url']
        followers = profile['user']['blogs'][0]['followers']
        bio = profile['user']['blogs'][0]['description']

        return cls(id, followers, bio=bio, profile_picture=profile_picture, original=profile)
