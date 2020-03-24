from flask_avatars import Avatars


def avatars_init(app):
    global avatars
    avatars = Avatars(app)
