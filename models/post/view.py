from .mentions import UserMention
from .embeds import *
from datetime import datetime
import os
import re
import requests
from bs4 import BeautifulSoup


class PostView:

    def __init__(self, original, id, timestamp, likes, shares, comments_count, text=None, hashtags=None, mentions=None,
                 embeds=None):
        self.__original = original

        self.__id = id
        self.__timestamp = timestamp

        self.__likes = likes
        self.__shares = shares
        self.__comments_count = comments_count

        self.__text = text
        self.__hashtags = hashtags
        self.__mentions = mentions
        self.__embeds = embeds

    def as_dict(self):
        post = {
            'id': self.__id,
            'created_at': self.__timestamp,
            'likes': self.__likes,
            'shares': self.__shares,
            'comments_count': self.__comments_count
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
        comments_count = 0  # TODO
        text = post['text']['text']
        hashtags = re.findall('#([^ .]+)', text)
        mentions = None  # TODO
        embeds = []

        if 'content' in post:
            for content in post['content']['contentEntities']:
                embeds.append(ImageEmbed(content['entityLocation']))

        return cls(post, id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags, embeds=embeds)

    @classmethod
    def from_tumblr(cls, post):
        id = post['id_string']
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

        return cls(post, id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags, embeds=embeds)

    @classmethod
    def from_twitter(cls, post):
        id = post['id_str']
        timestamp = datetime.strptime(post['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
        likes = post.get('favorite_count', 0)
        shares = post.get('retweet_count', 0)

        screen_name = post['user']['screen_name']
        html = requests.get(f'https://twitter.com/{screen_name}/status/{id}')
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
            embeds.append(QuoteEmbed(PostView.from_twitter(post['quoted_status'])))

        return cls(post, id, timestamp, likes, shares, comments_count, text=text, hashtags=hashtags, mentions=mentions,
                   embeds=embeds)
