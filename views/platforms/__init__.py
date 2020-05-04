from flask import Blueprint
import utils.auth as auth
from app import app

from .linkedin import LinkedInView
from .tumblr import TumblrView
from .twitter import TwitterView


def add_route(blueprint, route, func, **kwargs):
    blueprint.add_url_rule(route, func.__name__.replace('.', '::'), func, **kwargs)


def create_std_platform(platform_name, platform_cls, platform_auth_validator):
    platform_view = Blueprint(platform_name, platform_name, url_prefix=f'/{platform_name}')

    add_route(platform_view, '/auth', auth.platform_auth(platform_cls.auth))
    add_route(platform_view, '/auth/callback', auth.platform_callback(platform_cls.auth_callback))

    add_route(platform_view, '/profile', platform_auth_validator(platform_cls.profile))
    add_route(platform_view, '/profile/posts', platform_auth_validator(platform_cls.get_posts))
    add_route(platform_view, '/profile/posts/stats', platform_auth_validator(platform_cls.posts_stats))

    add_route(platform_view, '/post/<post_id>', platform_auth_validator(platform_cls.post_endpoint),
              methods=['GET', 'DELETE'])
    add_route(platform_view, '/post', platform_auth_validator(platform_cls.post), methods=['POST'])

    return platform_view


linkedin = create_std_platform('linkedin', LinkedInView, auth.linkedin_required)
add_route(linkedin, '/token', auth.verified_user_required(LinkedInView.get_token_exp))
app.register_blueprint(linkedin)

tumblr = create_std_platform('tumblr', TumblrView, auth.tumblr_required)
app.register_blueprint(tumblr)

twitter = create_std_platform('twitter', TwitterView, auth.twitter_required)
app.register_blueprint(twitter)
