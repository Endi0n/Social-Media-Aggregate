from models.api import LinkedInAPI
from models.database import User
from flask import Blueprint, redirect, request, jsonify
from utils.auth import login_required, linkedin_required
from app import app, db
from datetime import datetime
import bcrypt

auth = Blueprint(__name__, __name__, url_prefix='/auth')


@auth.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if len(password) < 7:
        return jsonify({'error': 'Password must be at least 7 characters long.'}), 400

    with User.query.filter_by(email=email).first() as user:
        if user:
            return jsonify({'error': 'There is already an account registered with this email.'}), 409

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password, salt)

    user = User(email, hash, name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration succeeded.'}), 201


@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Wrong email.'}), 401

    if not bcrypt.checkpw(password, user.password):
        return jsonify({'error': 'Wrong password.'}), 401