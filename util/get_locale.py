from flask import request
from util.json import validate_locale


def get_locale():
    locale = request.args.get('locale')
    if locale is not None:
        return validate_locale(locale)
    else:
        return validate_locale(request.headers.get('locale'))

