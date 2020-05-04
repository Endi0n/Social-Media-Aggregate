from flask_login import UserMixin
from sqlalchemy import Index
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    email = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email_validated = db.Column(db.Boolean, nullable=False, default=False)

    linkedin_token = db.relationship('LinkedInToken', backref='user', lazy=True, uselist=False)
    tumblr_token = db.relationship('TumblrToken', backref='user', lazy=True, uselist=False)
    twitter_token = db.relationship('TwitterToken', backref='user', lazy=True, uselist=False)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    @property
    def is_active(self):
        return self.email_validated


class LinkedInToken(db.Model):
    __tablename__ = 'linkedin_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, unique=True)
    token = db.Column(db.String(1000), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    expires_at = db.Column(db.DateTime)

    def __init__(self, user, token, expires_at):
        self.user_id = user.id
        self.token = token
        self.expires_at = expires_at


class TumblrToken(db.Model):
    __tablename__ = 'tumblr_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, unique=True)
    token = db.Column(db.String(1000), nullable=False)
    token_secret = db.Column(db.String(1000), nullable=False)

    def __init__(self, user, token, token_secret):
        self.user_id = user.id
        self.token = token
        self.token_secret = token_secret


class TwitterToken(db.Model):
    __tablename__ = 'twitter_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, unique=True)
    token = db.Column(db.String(1000), nullable=False)
    token_secret = db.Column(db.String(1000), nullable=False)

    def __init__(self, user, token, token_secret):
        self.user_id = user.id
        self.token = token
        self.token_secret = token_secret


class Platform(db.Model):
    __tablename__ = 'platform'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    platform = db.Column(db.String(10), nullable=False, unique=True)
    client_key = db.Column(db.String(50), nullable=False)
    client_secret = db.Column(db.String(50), nullable=False)


class FollowersCount(db.Model):
    __tablename__ = 'followers_count'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    followers = db.Column(db.Integer, nullable=False)
    automatic = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (Index('ix_followers_stat_user_id_platform_id_timestamp', 'user_id', 'platform_id', 'timestamp'),)
