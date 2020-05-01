import os


class PostView:

    def __init__(self, original, post_id, timestamp, likes, shares, comments_count, text=None, hashtags=None,
                 mentions=None, embeds=None):
        self._original = original

        self._post_id = post_id
        self._timestamp = timestamp

        self._likes = likes
        self._shares = shares
        self._comments_count = comments_count

        self._text = text
        self._hashtags = hashtags
        self._mentions = mentions
        self._embeds = embeds

    def as_dict(self):
        post = {
            'id': self._post_id,
            'created_at': self._timestamp,
            'likes': self._likes,
            'shares': self._shares,
            'comments_count': self._comments_count
        }

        if self._text:
            post['text'] = self._text

        if self._hashtags:
            post['hashtags'] = self._hashtags

        if self._mentions:
            post['mentions'] = [mention.as_dict() for mention in self._mentions]

        if self._embeds:
            post['embeds'] = [embed.as_dict() for embed in self._embeds]

        if self._original and os.getenv('DEBUG_POSTS'):
            post['original'] = self._original

        return post
