import datetime

from flask import Blueprint, g, request, abort, jsonify
from flask_jwt_extended import (
    set_access_cookies, create_access_token, get_jwt_identity,
    create_refresh_token, set_refresh_cookies,
    jwt_refresh_token_required, unset_jwt_cookies,
    jwt_required
)
from models.User import User
from models.UserRole import UserRole
from models.Role import Role
from flask_expects_json import expects_json
from models.base import get_session
import util.bcrypt_init


auth_blueprint = Blueprint('auth', __name__)


put_user_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
        'roles': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        }
    },
    'required': ['name', 'password', 'email', 'roles']
}


@auth_blueprint.route('/token/registration', methods=['PUT'])
@expects_json(put_user_schema)
def register_new_user():
    content = g.data
    session = get_session()

    users = session.query(User)

    username = content['name']
    if any(user.name == username for user in users):
        abort(400, "User with name = %s already exist" % username)
        return

    usermail = content['email']
    if any(user.email == usermail for user in users):
        abort(400, "User with email = %s already exist" % usermail)
        return

    roles = []

    for role_id in content['roles']:
        role = session.query(Role).get(role_id)

        if role is None:
            session.rollback()
            session.close()
            abort(400, "Role with id = %s not found" % role_id)
            return

        roles.append(role)

    session.add(User(
        name=content['name'],
        password=util.bcrypt_init.bcrypt.generate_password_hash(content['password']),
        email=content['email'],
        roles=roles
    ))

    session.commit()
    session.close()

    return 'ok'


@auth_blueprint.route('/token/registration', methods=['POST'])
@expects_json(put_user_schema)
@jwt_required
def update_user():
    content = g.data
    session = get_session()

    users = session.query(User)

    username = content['name']
    if any(user.name == username for user in users):
        abort(400, "User with name = %s already exist" % username)
        return

    usermail = content['email']
    if any(user.email == usermail for user in users):
        abort(400, "User with email = %s already exist" % usermail)
        return

    roles = []

    for role_id in content['roles']:
        role = session.query(Role).get(role_id)

        if role is None:
            session.rollback()
            session.close()
            abort(400, "Role with id = %s not found" % role_id)
            return

        roles.append(role)

    current_user_id = get_jwt_identity()

    user = session.query(User).filter(
        User.id == current_user_id
    ).first()

    user.name = content['name']
    user.password = util.bcrypt_init.bcrypt.generate_password_hash(content['password'])
    user.email = content['email']
    user.roles = roles

    session.commit()
    session.close()

    return 'ok'


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

    if not util.bcrypt_init.bcrypt.check_password_hash(user.password, password):
        abort(401, 'Invalid password')
        return

    expires = datetime.timedelta(days=5)
    access_token = create_access_token(identity=user.id, expires_delta=expires)
    refresh_token = create_refresh_token(identity=user.id, expires_delta=expires)
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
