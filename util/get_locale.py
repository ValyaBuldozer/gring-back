from flask import request, abort
from models.Language import Language
from util.json import validate_locale


def get_locale():
    locale = request.args.get('locale')
    if locale is not None:
        return validate_locale(locale)
    else:
        return validate_locale(request.headers.get('locale'))


def get_post_locale(session):
    locale = request.args.get('locale')
    if locale is None:
        locale = request.headers.get('locale')
        if locale is None:
            session.close()
            abort(400, "Locale must be specified either in search params or request header")
    if locale not in Language.__members__:
        session.close()
        abort(400, "%s is not a valid locale value" % locale)
    else:
        return Language[locale]
