from models.database import User
from flask import Blueprint, request, jsonify
import flask_login
from app import app, db
import utils.auth
import utils.request
import utils.mail
import utils.jwt
import bcrypt
import jwt
import re

auth = Blueprint(__name__, __name__, url_prefix='/auth')


@auth.route('/signup', methods=['POST'])
def signup():
    name = utils.request.form_get('name')
    email = utils.request.form_get('email')
    password = utils.request.form_get('password')

    if not re.fullmatch(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'):
        return jsonify(error='Invalid email.'), 400

    if len(password) < 7:
        return jsonify(error='Password must be at least 7 characters long.'), 400

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify(error='There is already an account registered with this email.'), 409

    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(password.encode(), salt).decode()

    user = User(email, pwd_hash, name)
    db.session.add(user)
    db.session.commit()

    utils.mail.send_validate_email(email, utils.jwt.generate_validate_email_token(user))

    return jsonify(message='Registration succeeded.'), 201


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user = utils.auth.get_authenticated_user()
        if not user:
            return jsonify(message='Unauthenticated.'), 401
        return jsonify(message='Authenticated.')

    if request.method == 'POST':
        email = utils.request.form_get('email')
        password = utils.request.form_get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify(error='Wrong email.'), 401

        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            return jsonify(error='Wrong password.'), 401

        flask_login.login_user(user, force=True)

        return jsonify(message='Authentication succeeded.')


@auth.route('/logout', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return jsonify(message='User logged out.')


@auth.route('/validate_email')
def validate_email():
    token_code = utils.request.args_get('token')

    token = jwt.decode(token_code.encode(), app.config['SECRET_KEY'])
    if token['request_type'] != 'validate_email':
        return jsonify(error='Wrong token type.'), 400

    user = User.query.get(token['user_id'])
    user.email_validated = True
    db.session.commit()

    return jsonify(message='Email validated successfully.')


@auth.route("/reset_password", methods=['POST'])
def reset_password():
    email = utils.request.form_get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(error='No account with specified email.'), 400

    token = utils.jwt.generate_reset_password_token(user)
    utils.mail.send_reset_password_email(email, token)

    return jsonify(message='Email sent succesfully.')


@auth.route('/reset_password/callback', methods=['POST'])
def reset_password_callback():
    token_code = utils.request.form_get('token')

    password = utils.request.form_get('password')

    if len(password) < 7:
        return jsonify(error='Password must be at least 7 characters long.'), 400

    token = jwt.decode(token_code.encode(), app.config['SECRET_KEY'])

    if token['request_type'] != 'reset_password':
        return jsonify(error='Wrong token type.'), 400

    user = User.query.get(token['user_id'])
    if not user:
        return jsonify(error='No account with specified email.'), 400

    if user.updated_at.timestamp() > int(token['iat']):
        return jsonify(message='Token expired.'), 403

    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(password.encode(), salt).decode()
    user.password = pwd_hash
    db.session.commit()

    return jsonify(message='Password reset succesfully.')
