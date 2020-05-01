from flask import Blueprint
from app import app
import utils.auth as auth

from .linkedin import LinkedInView
from .tumblr import TumblrView
from .twitter import TwitterView


def add_route(blueprint, route, func, **kwargs):
    blueprint.add_url_rule(route, func.__name__.replace('.', '::'), func, **kwargs)


def add_platform(platform_name, platform_cls, platform_auth_validator):
    platform_view = Blueprint(platform_name, platform_name, url_prefix=f'/{platform_name}')

    add_route(platform_view, '/auth', auth.platform_auth(platform_cls.auth))
    add_route(platform_view, '/auth/callback', auth.platform_callback(platform_cls.auth_callback))

    add_route(platform_view, '/profile', platform_auth_validator(platform_cls.profile))
    add_route(platform_view, '/profile/posts', platform_auth_validator(platform_cls.get_posts))

    add_route(platform_view, '/post/<post_id>', platform_auth_validator(platform_cls.post_endpoint),
              methods=['GET', 'DELETE'])
    add_route(platform_view, '/post', platform_auth_validator(platform_cls.post), methods=['POST'])

    app.register_blueprint(platform_view)


add_platform('linkedin', LinkedInView, auth.linkedin_required)
add_platform('tumblr', TumblrView, auth.tumblr_required)
add_platform('twitter', TwitterView, auth.twitter_required)
