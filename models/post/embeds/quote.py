class QuoteEmbed:

    def __init__(self, post):
        self.__post = post

    def as_dict(self):
        return {'type': 'quote', 'post': self.__post.as_dict()}
