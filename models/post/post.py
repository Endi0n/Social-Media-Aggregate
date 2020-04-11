from .mentions import UserMention
from .embeds import *
from datetime import datetime
import os
import re


class Post:

    def __init__(self, id, timestamp, likes, shares, text=None, hashtags=None, mentions=None, embeds=None,
                 original=None):
        self.__id = id
        self.__timestamp = timestamp

        self.__likes = likes
        self.__shares = shares

        self.__text = text
        self.__hashtags = hashtags
        self.__mentions = mentions
        self.__embeds = embeds

        self.__original = original

    def as_dict(self):
        post = {
            'id': self.__id,
            'created_at': self.__timestamp,
            'likes': self.__likes,
            'shares': self.__shares
        }

        if self.__text:
            post['text'] = self.__text

        if self.__hashtags:
            post['hashtags'] = self.__hashtags

        if self.__mentions:
            post['mentions'] = [mention.as_dict() for mention in self.__mentions]

        if self.__embeds:
            post['embeds'] = [embed.as_dict() for embed in self.__embeds]

        if self.__original and os.getenv('DEBUG_POSTS'):
            post['original'] = self.__original

        return post

    @classmethod
    def from_linkedin(cls, post):
        id = post['id']
        timestamp = post['created']['time'] // 1e3
        likes = 0  # TODO
        shares = 0  # TODO
        text = post['text']['text']
        hashtags = re.findall('#([^ .])', text)
        mentions = None  # TODO
        embeds = []

        if 'content' in post:
            for content in post['content']['contentEntities']:
                embeds.append(ImageEmbed(content['entityLocation']))

        return Post(id, timestamp, likes, shares, text=text, hashtags=hashtags, embeds=embeds, original=post)

    @classmethod
    def from_tumblr(cls, post):
        id = post['id']
        timestamp = post['created_at']
        likes = post['likes']
        shares = post['reblogs']
        text = 'dummy text' # TODO
        hashtags = post['hashtags']
        # embeds  # TODO
        original = 'dummy original'
        return Post(id, timestamp, likes, shares, text=text, hashtags=hashtags, original=original)

    @classmethod
    def from_twitter(cls, post):
        id = post['id_str']
        timestamp = datetime.strptime(post['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
        likes = post['favorite_count']
        shares = post['retweet_count']
        text = post['full_text']  # TODO: remove trailing link
        hashtags = [tag['text'] for tag in post['hashtags']]
        mentions = [UserMention(user['id'], name=user['name'], tag=user['tag']) for user in post['user_mentions']]
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
            embeds.append(QuoteEmbed(Post.from_twitter(post['quoted_status'])))

        return Post(id, timestamp, likes, shares, text=text, hashtags=hashtags, mentions=mentions, embeds=embeds,
                    original=post)
