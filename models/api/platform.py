from abc import ABC


class PlatformAPI(ABC):

    def get_profile(self):
        raise NotImplementedError

    def get_post(self, post_id):
        raise NotImplementedError

    def get_posts(self):
        raise NotImplementedError

    def post(self, post_draft):
        raise NotImplementedError

    def delete_post(self, post_id):
        raise NotImplementedError

    def posts_stats(self):
        posts = self.get_posts()['posts']

        likes = []
        shares = []
        comments = []

        for post in posts:
            likes.append(post['likes'])
            shares.append(post['shares'])
            comments.append(post['comments_count'])

        likes_sum = sum(likes)
        shares_sum = sum(shares)
        comments_sum = sum(comments)

        likes_no = len(likes) if likes else 1
        shares_no = len(shares) if shares else 1
        comments_no = len(comments) if comments else 1

        stats = {
            'likes_sum': likes_sum,
            'shares_sum': shares_sum,
            'comments_sum': comments_sum,

            'likes_avg': likes_sum / likes_no,
            'shares_avg': shares_sum / shares_no,
            'comments_avg': comments_sum / comments_no
        }

        return stats

    def get_posts_ranked(self, ranking_key):
        return {'posts': sorted(self.get_posts()['posts'], key=lambda post: post[ranking_key], reverse=True)}
