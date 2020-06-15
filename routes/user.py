import os
from uuid import uuid4
from flask import Blueprint, g, request, abort, jsonify, current_app
from flask_avatars import Identicon
from models.Entity import Entity
from models.Place import Place
from util.avatars_init import get_default_avatar
from util.get_locale import validate_locale, get_locale
from util.json import convert_to_json, returns_json
from flask_jwt_extended import get_jwt_identity
from models.base import get_session
from models.User import User
from models.RoleName import RoleName
from util.decorators import roles_required
from util.current_user import get_current_user
from models.Role import Role
from flask_expects_json import expects_json
from email.utils import parseaddr

from util.image_service import upload_image, delete_image


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user', methods=['GET'])
@roles_required([RoleName.user])
@returns_json
def get_current_user():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    json_user = convert_to_json(user)

    session.close()

    return json_user


put_user_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
        'image': {'type': 'string'},
    },
    'required': ['username', 'password', 'email']
}

post_user_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
        'image': {'type': 'string'},
    }
}


@user_blueprint.route('/user', methods=['PUT'])
@expects_json(put_user_schema)
def basic_register_new_user():
    content = g.data
    session = get_session()

    users = session.query(User).all()

    username = content['username']
    if any(user.name == username for user in users):
        session.close()
        abort(409, "User with name = %s already exist" % username)
        return

    email = content['email']
    if '@' not in parseaddr(email)[1]:
        session.close()
        abort(400, "Invalid email")
        return
    if any(user.email == email for user in users):
        session.close()
        abort(409, "User with email = %s already exist" % email)
        return

    roles = [session.query(Role).filter(
        Role.name == RoleName.user.name
    ).first()]

    if 'image' in content:
        image = content['image']
    else:
        image = get_default_avatar(username)

    user = User(
        name=username,
        email=email,
        roles=roles,
        image=image
    )

    user.set_password(content['password'])

    session.add(user)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user', methods=['POST'])
@expects_json(post_user_schema)
@roles_required([RoleName.user])
def basic_update_user():
    content = g.data
    session = get_session()

    users = session.query(User).all()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % current_user_id)
        return

    users = [u for u in users if u.id is not user.id]

    if 'username' in content:
        if any(user.name == content['username'] for user in users):
            session.close()
            abort(409, "User with name = %s already exist" % content['username'])
            return
        else:
            user.name = content['username']

    if 'email' in content:
        email = content['email']
        if '@' not in parseaddr(email)[1]:
            session.close()
            abort(400, "Invalid email")
            return
        if any(user.email == email for user in users):
            session.close()
            abort(409, "User with email = %s already exist" % email)
            return
        else:
            user.email = email

    if 'password' in content:
        user.set_password(content['password'])

    if 'image' in content:
        user.image = content['image']

    session.commit()
    session.close()

    return 'ok'


def delete_user_by_id(user_id):
    session = get_session()
    user = session.query(User).get(user_id)

    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)
        return

    if user.is_admin():
        session.close()
        abort(400, "User with id = %s cannot be deleted" % user_id)
        return

    session.delete(user)
    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/favorite', methods=['GET'])
@roles_required([RoleName.user])
@returns_json
def get_user_favorite_by_id():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)
    locale = get_locale()

    json_favorites = convert_to_json(
        list(map(lambda entity: entity.to_entity_json(locale), user.favorites))
     )

    session.close()

    return json_favorites


put_favorite_schema = {
    'type': 'object',
    'properties': {
        'entity_id': {'type': 'integer'},
    },
    'required': ['entity_id']
}


@user_blueprint.route('/user/favorite', methods=['POST'])
@expects_json(put_favorite_schema)
@roles_required([RoleName.user])
def add_new_favorite():
    content = g.data
    session = get_session()

    entity_id = content['entity_id']
    favorite = session.query(Entity).get(entity_id)

    if favorite is None:
        session.close()
        abort(400, "Entity with id = %s not found" % entity_id)
        return

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    if any(entity.id == favorite.id for entity in user.favorites):
        session.close()
        abort(409, "Entity with id = %s already added to favorites" % favorite.id)
        return

    user.favorites.append(favorite)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/favorite/<entity_id>', methods=['DELETE'])
@roles_required([RoleName.user])
def delete_favorite(entity_id):
    session = get_session()
    favorite = session.query(Entity).get(entity_id)

    if favorite is None:
        session.close()
        abort(404, "Entity with id = %s not found" % entity_id)
        return

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    user.favorites.remove(favorite)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/visited', methods=['GET'])
@roles_required([RoleName.user])
@returns_json
def get_user_visited_by_id():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)
    locale = get_locale()

    json_visited_places = convert_to_json(
        list(map(lambda entity: entity.to_entity_json(locale), user.visited_places))
     )

    session.close()

    return json_visited_places


put_visited_place_schema = {
    'type': 'object',
    'properties': {
        'place_id': {'type': 'integer'},
    },
    'required': ['place_id']
}


@user_blueprint.route('/user/visited', methods=['POST'])
@expects_json(put_visited_place_schema)
@roles_required([RoleName.user])
def add_new_visited_place():
    content = g.data
    session = get_session()

    place_id = content['place_id']
    visited_place = session.query(Place).get(place_id)

    if visited_place is None:
        session.close()
        abort(400, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    if any(entity.id == visited_place.id for entity in user.visited_places):
        session.close()
        abort(409, "Place with id = %s already added to visited places" % visited_place.id)
        return

    user.visited_places.append(visited_place)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/visited/<place_id>', methods=['DELETE'])
@roles_required([RoleName.user])
def delete_visited_place(place_id):
    session = get_session()
    visited_place = session.query(Place).get(place_id)

    if visited_place is None:
        session.close()
        abort(404, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    user.visited_places.remove(visited_place)

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/image', methods=['POST'])
@roles_required([RoleName.user])
def upload_user_image():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    filename = upload_image(user.image)

    user.image = filename

    session.commit()
    session.close()

    return filename


@user_blueprint.route('/user/image', methods=['DELETE'])
@roles_required([RoleName.user])
def delete_user_image():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    if user.image is not None:
        delete_image(user.image)
        user.image = get_default_avatar(user.name)
    else:
        return abort(400, 'User has no avatar to delete')

    session.commit()
    session.close()

    return 'ok'

