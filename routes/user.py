from flask import Blueprint, g, request, abort, jsonify
from util.json import to_json
from flask_jwt_extended import get_jwt_identity
from models.base import get_session
from models.User import User
from models.Place import Place
from models.RoleName import RoleName
from util.decorators import roles_required
from util.current_user import get_current_user
from models.Role import Role
from flask_expects_json import expects_json
from util import bcrypt_init


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user/favorite', methods=['GET'])
@roles_required([RoleName.content_moder, RoleName.user_moder, RoleName.user])
def get_user_favorite_place_by_id():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    json_place = to_json(user.favorite_places)

    session.close()

    return json_place


@user_blueprint.route('/user/block/<user_id>', methods=['POST'])
@roles_required([RoleName.user_moder])
def block_user_by_id(user_id):
    session = get_session()

    user = session.query(User).get(user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)
        return

    if user.is_admin():
        session.close()
        abort(400, "User with id = %s cannot be blocked" % user_id)
        return

    user.is_active = False

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/unblock/<user_id>', methods=['POST'])
@roles_required([RoleName.user_moder])
def unblock_user_by_id(user_id):
    session = get_session()

    user = session.query(User).get(user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)

    if user.is_active:
        session.close()
        abort(400, "User with id = %s is already active" % user_id)
        return

    user.is_active = True

    session.commit()
    session.close()

    return 'ok'


put_favorite_schema = {
    'type': 'object',
    'properties': {
        'place_id': {'type': 'integer'},
    },
    'required': ['place_id']
}


@user_blueprint.route('/user/favorite', methods=['POST'])
@expects_json(put_favorite_schema)
@roles_required([RoleName.content_moder, RoleName.user_moder, RoleName.user])
def add_new_favorite_place():
    content = g.data
    session = get_session()

    place_id = content['place_id']
    favorite_place = session.query(Place).get(place_id)

    if favorite_place is None:
        session.close()
        abort(400, "Place with id = %s not found" % place_id)
        return

    user = get_current_user()

    if any(place.id == favorite_place.id for place in user.favorite_places):
        session.close()
        abort(400, "Place with id = %s already added to favorites" % favorite_place.id)
        return

    user.favorite_places.append(favorite_place)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/favorite/<place_id>', methods=['DELETE'])
@roles_required([RoleName.content_moder, RoleName.user_moder, RoleName.user])
def delete_favorite_place(place_id):
    session = get_session()
    favorite_place = session.query(Place).get(place_id)

    if favorite_place is None:
        session.close()
        abort(404, "Place with id = %s not found" % place_id)
        return

    user = get_current_user()

    user.favorite_places.remove(favorite_place)

    session.commit()
    session.close()

    return 'ok'


put_user_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
    },
    'required': ['name', 'password', 'email']
}

post_user_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
    }
}


@user_blueprint.route('/user/registration', methods=['PUT'])
@expects_json(put_user_schema)
def basic_register_new_user():
    content = g.data
    session = get_session()

    users = session.query(User).all()

    username = content['name']
    if any(user.name == username for user in users):
        session.close()
        abort(400, "User with name = %s already exist" % username)
        return

    usermail = content['email']
    if any(user.email == usermail for user in users):
        session.close()
        abort(400, "User with email = %s already exist" % usermail)
        return

    roles = [session.query(Role).get(RoleName.user.value)]

    session.add(User(
        name=content['name'],
        password=bcrypt_init.bcrypt.generate_password_hash(content['password']),
        email=content['email'],
        roles=roles
    ))

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/update', methods=['POST'])
@expects_json(post_user_schema)
@roles_required([RoleName.content_moder, RoleName.user_moder, RoleName.user])
def basic_update_user():
    content = g.data
    session = get_session()

    users = session.query(User).all()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    users = [u for u in users if u.id is not user.id]

    if 'name' in content:
        if any(user.name == content['name'] for user in users):
            session.close()
            abort(400, "User with name = %s already exist" % content['name'])
            return
        else:
            user.name = content['name']

    if 'email' in content:
        if any(user.email == content['email'] for user in users):
            session.close()
            abort(400, "User with email = %s already exist" % content['email'])
            return
        else:
            user.email = content['email']

    if 'password' in content:
        user.password = bcrypt_init.bcrypt.generate_password_hash(content['password'])

    session.commit()
    session.close()

    return 'ok'
