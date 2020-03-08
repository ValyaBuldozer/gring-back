from models.Object import Object
from models.Category import Category
from flask import Blueprint, request, abort
from util.json import convert_to_json, returns_json, validate_locate
from models.base import get_session


object_blueprint = Blueprint('objects', __name__)


@object_blueprint.route('/objects', methods=['GET'])
@returns_json
def get_objects():
    session = get_session()

    objects = session.query(Object).all()

    locale = validate_locate(request.headers.get('locale'))
    mapped_objects = list(map(lambda o: o.to_base_json(locale), objects))

    json_objects = convert_to_json(mapped_objects, locale)

    session.close()

    return json_objects


@object_blueprint.route('/objects/<object_id>', methods=['GET'])
@returns_json
def get_object_by_id(object_id):
    session = get_session()

    obj = session.query(Object).get(object_id)

    if obj is None:
        session.close()
        abort(404, "Object with id = %s not found" % object_id)

    locale = validate_locate(request.headers.get('locale'))
    json_object = convert_to_json(obj, locale)

    session.close()

    return json_object
