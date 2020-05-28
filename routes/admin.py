import os
from uuid import uuid4
from flask import Blueprint, g, request, abort, jsonify, current_app
from flask_avatars import Identicon
from models.Review import Review
from util.audio_service import upload_audio
from util.avatars_init import get_default_avatar
from util.json import convert_to_json
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
from util.image_service import upload_image, delete_image

admin_blueprint = Blueprint('admin', __name__)


put_user_admin_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
        'roles': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        },
        'image': {'type': 'string'}
    },
    'required': ['username', 'password', 'email', 'roles']
}

post_user_admin_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'},
        'roles': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        },
        'image': {'type': 'string'}
    }
}


@admin_blueprint.route('/admin/users', methods=['PUT'])
@expects_json(put_user_admin_schema)
@roles_required([RoleName.user_moder])
def admin_register_new_user():
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

    roles = []

    for role_id in content['roles']:
        role = session.query(Role).get(RoleName(role_id).value)

        if role is None:
            session.close()
            abort(400, "Role with id = %s not found" % role_id)
            return

        roles.append(role)

    roles = [session.query(Role).get(RoleName.user.value)]

    if 'image' in content:
        image = content['image']
    else:
        image = get_default_avatar(username)

    session.add(User(
        name=content['username'],
        password=bcrypt_init.bcrypt.generate_password_hash(content['password']),
        email=content['email'],
        roles=roles,
        image=image
    ))

    session.commit()
    session.close()

    return 'ok'


@admin_blueprint.route('/admin/users/<user_id>', methods=['POST'])
@expects_json(post_user_admin_schema)
@roles_required([RoleName.user_moder])
def admin_update_user(user_id):
    content = g.data
    session = get_session()

    users = session.query(User).all()

    user = session.query(User).get(user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)
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

    roles = []

    if 'roles' in content:
        for role_id in content['roles']:
            role = session.query(Role).get(RoleName(role_id).value)

            if role is None:
                session.close()
                abort(400, "Role with id = %s not found" % role_id)
                return

            roles.append(role)

    if 'password' in content:
        user.password = bcrypt_init.bcrypt.generate_password_hash(content['password'])

    if 'image' in content:
        user.image = content['image']

    user.roles = roles

    session.commit()
    session.close()

    return 'ok'


@admin_blueprint.route('/admin/avatars/<user_id>', methods=['DELETE'])
@roles_required([RoleName.user_moder])
def admin_delete_avatar_by_user_id(user_id):
    session = get_session()

    user = session.query(User).get(user_id)

    if user.image is not None:
        delete_image(user.image)
        user.image = get_default_avatar(user.name)
    else:
        return abort(400, 'User has no avatar to delete')

    session.commit()
    session.close()

    return 'ok'


delete_review_schema = {
    'type': 'object',
    'properties': {
        'user_id': {'type': 'integer'},
        'entity_id': {'type': 'integer'}
    },
    'required': ['user_id', 'entity_id']
}


@admin_blueprint.route('/admin/reviews', methods=['DELETE'])
@expects_json(delete_review_schema)
@roles_required([RoleName.user_moder])
def delete_user_review():
    content = g.data
    session = get_session()

    user_id = content['user_id']
    entity_id = content['entity_id']
    review = session.query(Review).filter(
        Review.user_id == user_id,
        Review.entity_id == entity_id
    ).first()

    if review is None:
        session.close()
        abort(404, "User with id = %s didn't add review to entity with id = %s yet" % (user_id, entity_id))
        return

    session.delete(review)
    session.commit()
    session.close()

    return 'ok'


@admin_blueprint.route('/admin/block/<user_id>', methods=['POST'])
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


@admin_blueprint.route('/admin/unblock/<user_id>', methods=['POST'])
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


@admin_blueprint.route('/admin/images', methods=['PUT'])
@roles_required([RoleName.user_moder, RoleName.content_moder])
def put_image():
    filename = upload_image(old_image=None)

    return filename


@admin_blueprint.route('/admin/audios', methods=['PUT'])
@roles_required([RoleName.user_moder, RoleName.content_moder])
def put_audio():
    filename = upload_audio(old_audio=None)

    return filename
