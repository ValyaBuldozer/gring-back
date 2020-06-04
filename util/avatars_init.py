import os
from uuid import uuid4
from flask import current_app
from flask_avatars import Avatars, Identicon


def avatars_init():
    global avatars
    avatars = Avatars(current_app)


def get_default_avatar(username):
    avatar = Identicon()
    path = current_app.config['ASSETS_PATH']
    filename = '%s.png' % str(uuid4())
    size = current_app.config['AVATAR_SIZE']

    image_byte_array = avatar.get_image(
        string=username,
        width=int(size),
        height=int(size),
        pad=int(size * 0.1))
    avatar.save(image_byte_array, save_location=os.path.join(path, filename))

    return filename

