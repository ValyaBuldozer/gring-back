from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import (
    set_access_cookies, create_access_token, get_jwt_identity,
    create_refresh_token, set_refresh_cookies,
    jwt_refresh_token_required, unset_jwt_cookies
)
from models.User import User


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/token/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter(
        User.name == username
    ).first()

    if user is None:
        abort(401, 'User not found')
        return

    if user.password != password:
        abort(401, 'Invalid password')
        return

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
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
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)

    return resp, 200
