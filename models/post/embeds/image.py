class ImageEmbed:

    def __init__(self, url):
        self.__url = url

    def as_dict(self):
        return {'type': 'image', 'url': self.__url}
