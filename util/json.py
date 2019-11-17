import json
from flask import Response
from functools import wraps


def to_json(obj, lam=lambda o: o.to_json()):
    return json.dumps(
        obj,
        default=lam,
        ensure_ascii=False,
        indent=4
    )


def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json')
    return decorated_function
    