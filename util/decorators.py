from models.User import User
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from functools import wraps
from flask import abort
from util.current_user import get_current_user


def roles_required(roles):
    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user.can(roles):
                abort(403, "Access error")
            return f(*args, **kwargs)

        return decorated_function
    return decorator


