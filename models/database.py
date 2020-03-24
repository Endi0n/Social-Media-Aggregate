from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(50), nullable=False)

    linkedin_token = db.relationship('linkedin_token', backref='user_id', lazy=True)
    tumblr_token = db.relationship('tumblr_token', backref='user_id', lazy=True)
    twitter_token = db.relationship('twitter_token', backref='user_id', lazy=True)


class LinkedInToken(db.Model):
    __tablename__ = 'linkedin_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(1000))
    updated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)


class TumblrToken(db.Model):
    __tablename__ = 'tumblr_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(1000))
    updated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)


class TwitterToken(db.Model):
    __tablename__ = 'twitter_token'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(1000))
    token_secret = db.Column(db.String(1000))
    updated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)


class AppKey(db.Model):
    __tablename__ = 'app_key'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    platform_id = db.Column(db.String(10), nullable=False, unique=True)
    client_key = db.Column(db.String(50), nullable=False)
    client_secret = db.Column(db.String(50), nullable=False)
