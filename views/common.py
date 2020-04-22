from flask import jsonify
from utils.auth import verified_user_required
from app import app


@app.route('/profile')
@verified_user_required
def profile(user):
    return jsonify(id=user.id)
