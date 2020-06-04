from flask import current_app
from flask_bcrypt import Bcrypt


def bcrypt_init():
    global bcrypt
    bcrypt = Bcrypt(current_app)
