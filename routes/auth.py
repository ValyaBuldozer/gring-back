import datetime

from flask import Blueprint, g, request, abort, jsonify
from flask_jwt_extended import (
    set_access_cookies, create_access_token, get_jwt_identity,
    create_refresh_token, set_refresh_cookies,
    jwt_refresh_token_required, unset_jwt_cookies,
    jwt_required
)
from models.User import User
from models.base import get_session
from util import bcrypt_init
from flask import current_app
from flask_expects_json import expects_json


auth_blueprint = Blueprint('auth', __name__)


auth_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'}
    },
    'required': ['username', 'password']
}


@auth_blueprint.route('/token/auth', methods=['POST'])
@expects_json(auth_schema)
def login():
    content = g.data
    session = get_session()

    username = content['username']
    password = content['password']

    user = session.query(User).filter(
        User.name == username
    ).first()

    session.close()

    if user is None:
        abort(401, 'User not found')
        return

    if not user.is_active:
        abort(403, 'User has been banned')
        return

    if not bcrypt_init.bcrypt.check_password_hash(user.password, password):
        abort(401, 'Invalid password')
        return

    at_expires = datetime.timedelta(days=current_app.config['ACCESS_TOKEN_EXPIRES_DAYS'])
    access_token = create_access_token(identity=user.id, expires_delta=at_expires)
    rt_expires = datetime.timedelta(days=current_app.config['REFRESH_TOKEN_EXPIRES_DAYS'])
    refresh_token = create_refresh_token(identity=user.id, expires_delta=rt_expires)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp


@auth_blueprint.route('/token/remove', methods=['POST'])
def remove_token():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@auth_blueprint.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh_token():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)

    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)

    return resp, 200
