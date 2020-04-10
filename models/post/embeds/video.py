class VideoEmbed:

    def __init__(self, url, cover_url=None, duration=None):
        self.__url = url
        self.__cover_url = cover_url
        self.__duration = duration

    def as_dict(self):
        video_json = {'type': 'video', 'url': self.__url}

        if self.__cover_url:
            video_json['cover_url'] = self.__cover_url

        if self.__duration:
            video_json['duration'] = self.__duration

        return video_json
