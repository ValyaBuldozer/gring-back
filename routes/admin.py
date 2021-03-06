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
from util.image_service import upload_image, delete_image
from email.utils import parseaddr


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
@roles_required([RoleName.admin, RoleName.user_moder])
def admin_register_new_user():
    content = g.data
    session = get_session()

    users = session.query(User).all()

    username = content['username']
    if any(user.name == username for user in users):
        session.close()
        abort(400, "User with name = %s already exist" % username)
        return

    email = content['email']
    if '@' not in parseaddr(email)[1]:
        session.close()
        abort(400, "Invalid email")
        return
    if any(user.email == email for user in users):
        session.close()
        abort(400, "User with email = %s already exist" % email)
        return

    roles = []

    for role_id in content['roles']:
        role = session.query(Role).get(role_id)

        if role is None:
            session.close()
            abort(400, "Role with id = %s not found" % role_id)
            return

        current_user_id = get_jwt_identity()
        user = session.query(User).get(current_user_id)
        moder_roles = [RoleName.admin.value, RoleName.content_moder.value, RoleName.user_moder.value]
        if role.id in moder_roles and not user.is_admin():
            session.close()
            abort(403, "Not enough rights to register user with role = %s" % role_id)
            return

        roles.append(role)

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


@admin_blueprint.route('/admin/users/<user_id>', methods=['POST'])
@expects_json(post_user_admin_schema)
@roles_required([RoleName.admin, RoleName.user_moder])
def admin_update_user(user_id):
    content = g.data
    session = get_session()

    users = session.query(User).all()

    user = session.query(User).get(user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)
        return

    current_user_id = get_jwt_identity()
    author = session.query(User).get(current_user_id)

    if user.is_admin() and not user.id == author.id:
        session.close()
        abort(404, "User with id = %s cannot be updated" % user_id)
        return

    if user.is_moder() and not author.is_admin() and not user.id == author.id:
        session.close()
        abort(403, "Not enough rights to update user with id = %s" % user_id)
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
        email = content['email']
        if '@' not in parseaddr(email)[1]:
            session.close()
            abort(400, "Invalid email")
            return
        if any(user.email == email for user in users):
            session.close()
            abort(400, "User with email = %s already exist" % email)
            return
        else:
            user.email = email

    if 'roles' in content:
        roles = []
        for role_id in content['roles']:
            role = session.query(Role).get(RoleName(role_id).value)

            if role is None:
                session.close()
                abort(400, "Role with id = %s not found" % role_id)
                return

            roles.append(role)

        user.roles = roles

    if 'password' in content:
        user.set_password(content['password'])

    if 'image' in content:
        user.image = content['image']

    session.commit()
    session.close()

    return 'ok'


@admin_blueprint.route('/admin/avatars/<user_id>', methods=['DELETE'])
@roles_required([RoleName.admin, RoleName.user_moder])
def admin_delete_avatar_by_user_id(user_id):
    session = get_session()

    user = session.query(User).get(user_id)

    current_user_id = get_jwt_identity()
    author = session.query(User).get(current_user_id)

    if user.is_admin() and not user.id == author.id:
        session.close()
        abort(404, "Avatar which belongs to user with id = %s cannot be deleted" % user_id)
        return

    if user.is_moder() and not author.is_admin() and not user.id == author.id:
        session.close()
        abort(403, "Not enough rights to delete avatar which belongs to user with id = %s" % user_id)
        return

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
@roles_required([RoleName.admin, RoleName.user_moder])
def delete_user_review():
    content = g.data
    session = get_session()

    user_id = content['user_id']
    user = session.query(User).get(user_id)

    current_user_id = get_jwt_identity()
    author = session.query(User).get(current_user_id)

    if user.is_admin() and not user.id == author.id:
        session.close()
        abort(404, "Review which belongs to user with id = %s cannot be deleted" % user_id)
        return

    if user.is_moder() and not author.is_admin() and not user.id == author.id:
        session.close()
        abort(403, "Not enough rights to delete review which belongs to user with id = %s" % user_id)
        return

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
@roles_required([RoleName.admin, RoleName.user_moder])
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
@roles_required([RoleName.admin, RoleName.user_moder])
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


@admin_blueprint.route('/admin/reviews/<user_id>', methods=['DELETE'])
@roles_required([RoleName.admin, RoleName.user_moder])
def delete_all_user_reviews(user_id):
    session = get_session()

    user = session.query(User).get(user_id)
    if user is None:
        session.close()
        abort(404, "User with id = %s not found" % user_id)

    if user.is_admin():
        session.close()
        abort(400, "Reviews which belongs to user with id = %s cannot be deleted" % user_id)
        return

    session.query(Review).filter(
        Review.user_id == user_id,
    ).delete()

    session.commit()
    session.close()

    return 'ok'


@admin_blueprint.route('/admin/images', methods=['PUT'])
@roles_required([RoleName.admin, RoleName.user_moder, RoleName.content_moder])
def put_image():
    filename = upload_image(old_image=None)

    return filename


@admin_blueprint.route('/admin/audios', methods=['PUT'])
@roles_required([RoleName.admin, RoleName.user_moder, RoleName.content_moder])
def put_audio():
    filename = upload_audio(old_audio=None)

    return filename
