from flask_bcrypt import Bcrypt


def bcrypt_init(app):
    global bcrypt
    bcrypt = Bcrypt(app)
