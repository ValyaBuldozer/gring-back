import os
import uuid

from flask import Blueprint, g, request, abort, jsonify, current_app

from models.Entity import Entity
from util.json import convert_to_json
from flask_jwt_extended import get_jwt_identity
from models.base import get_session
from models.User import User
from models.RoleName import RoleName
from util.decorators import roles_required
from util.current_user import get_current_user
from models.Role import Role
from flask_expects_json import expects_json
from util import bcrypt_init


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user/favorite', methods=['GET'])
@roles_required([RoleName.user])
def get_user_favorite_by_id():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    json_favorites = convert_to_json(user.favorites)

    session.close()

    return json_favorites


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
        abort(400, "Entity with id = %s already added to favorites" % favorite.id)
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


put_user_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
    },
    'required': ['username', 'password', 'email']
}

post_user_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
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

    username = content['username']
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
        name=content['username'],
        password=bcrypt_init.bcrypt.generate_password_hash(content['password']),
        email=content['email'],
        roles=roles
    ))

    session.commit()
    session.close()

    return 'ok'


@user_blueprint.route('/user/update', methods=['POST'])
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
            abort(400, "User with name = %s already exist" % content['username'])
            return
        else:
            user.name = content['username']

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


@user_blueprint.route('/user/image', methods=['POST'])
@roles_required([RoleName.user])
def upload_image():
    session = get_session()

    if 'image' not in request.files:
        return abort(400, 'No file to save')

    image = request.files['image']

    if image.filename == '':
        return abort(400, 'No files to save')

    ext = image.filename.rsplit('.', 1)[::-1][0]

    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return abort(400, 'This file type is not allowed')

    image.filename = str(uuid.uuid1()) + '.' + ext
    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    image.save(os.path.join(current_path, assets_path, image.filename))

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    if user.image is not None:
        path = os.path.join(current_path, assets_path, user.image)
        if os.path.isfile(path):
            os.remove(os.path.join(current_path, assets_path, user.image))

    user.image = image.filename

    session.commit()
    session.close()

    return 'assets/' + image.filename


@user_blueprint.route('/user/image', methods=['DELETE'])
@roles_required([RoleName.user])
def delete_image():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    if user.image is not None:
        path = os.path.join(current_path, assets_path, user.image)
        if os.path.isfile(path):
            os.remove(os.path.join(current_path, assets_path, user.image))
        user.image = None
    else:
        return abort(400, 'User has no picture to delete')

    session.commit()
    session.close()

    return 'ok'
