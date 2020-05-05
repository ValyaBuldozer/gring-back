import json
from flask import Response
from functools import wraps
from models.Language import Language


def convert_to_json(obj, locale=Language.ru):
    return json.dumps(
        obj,
        default=lambda o: o.to_json(locale),
        ensure_ascii=False,
        indent=4
    )


def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json')
    return decorated_function
