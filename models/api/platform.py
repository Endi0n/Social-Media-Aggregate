from abc import ABC


class PlatformAPI(ABC):

    def get_profile(self):
        raise NotImplementedError

    def get_post(self, post_id):
        raise NotImplementedError

    def get_posts(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def delete_post(self, post_id):
        raise NotImplementedError
