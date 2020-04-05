from models.database import User
from flask import Blueprint, request, jsonify
import flask_login
from app import app, db
import utils.mail
import utils.jwt
import bcrypt
import jwt

auth = Blueprint(__name__, __name__, url_prefix='/auth')


@auth.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if len(password) < 7:
        return jsonify(error='Password must be at least 7 characters long.'), 400

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify(error='There is already an account registered with this email.'), 409

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode(), salt).decode()

    user = User(email, hash, name)
    db.session.add(user)
    db.session.commit()

    utils.mail.send_validate_email(email, utils.jwt.generate_validate_email_token(user))

    return jsonify(message='Registration succeeded.'), 201


@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(error='Wrong email.'), 401

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify(error='Wrong password.'), 401

    flask_login.login_user(user)

    return jsonify(message='Authentication succeeded.')


@auth.route('/logout', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()


@auth.route('/validate_email')
def validate_email():
    token_code = request.args.get('token')
    if not token_code:
        return jsonify(error='Token parameter missing.'), 400

    token = jwt.decode(token_code.encode(), app.config['SECRET_KEY'])
    if token['request_type'] != 'validate_email':
        return jsonify(error='Wrong token type.'), 400

    user = User.query.get(token['user_id'])
    user.email_validated = True
    db.session.commit()

    return jsonify(message='Email validated successfully.'), 200



@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        token = utils.jwt.generate_reset_password_token(user)
        utils.mail.send_reset_password_email(email, token)
        return jsonify({'message': 'Email sent succesfully'}), 200

    elif request.method == "GET":
        token = jwt.decode(request.args.get('token').encode(), app.config['SECRET_KEY'])

        user = User.query.get(token['user_id'])
        if user.update_at > token['timestamp']:
            return jsonify({'message': 'Token expired'}), 403

        user.password = bcrypt(request.form.get('password'))
        user.update_at = datetime.now()
        db.session.commit()

        return jsonify({'message': 'Password reset succesfully'}), 200
