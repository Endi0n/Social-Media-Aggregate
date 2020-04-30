from flask import jsonify
from utils.auth import verified_user_required
from app import app
import utils.jwt


@app.route('/profile')
@verified_user_required
def profile(user):
    return jsonify(id=user.id)


@app.route('/token')
@verified_user_required
def token(user):
    return jsonify(token=utils.jwt.generate_token(user))
