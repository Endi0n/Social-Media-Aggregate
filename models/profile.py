import os


class Profile:

    def __init__(self, original, profile_id, followers, name=None, bio=None, profile_picture=None, pages=None):
        self._original = original
        self._profile_id = profile_id
        self._followers = followers
        self._name = name
        self._bio = bio
        self._profile_picture = profile_picture
        self._pages = pages

        self._original = original

    def as_dict(self):
        profile = {
            'id': self._profile_id,
            'followers': self._followers,
        }

        if self._name:
            profile['name'] = self._name

        if self._bio:
            profile['bio'] = self._bio

        if self._profile_picture:
            profile['profile_picture'] = self._profile_picture

        if self._pages:
            profile['pages'] = self._pages

        if self._original and os.getenv('DEBUG_PROFILE'):
            profile['original'] = self._original

        return profile
