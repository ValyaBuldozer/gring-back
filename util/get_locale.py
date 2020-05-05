from flask import request, abort
from models.Language import Language


def validate_locale(locale):
    if locale is None or locale not in Language.__members__:
        return Language.ru

    return Language[locale]


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
