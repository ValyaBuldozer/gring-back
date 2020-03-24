from flask import Blueprint, current_app

from models.User import User
from models.base import get_session
from util.avatars_init import get_default_avatar


avatar_command_blueprint = Blueprint('avatar', __name__)


@avatar_command_blueprint.cli.command("create-default")
def create_default():
    session = get_session()

    users = session.query(User).all()

    for user in users:
        if user.image is None:
            user.image = get_default_avatar(user.name)

    session.commit()
    session.close()

    print('Ok')
