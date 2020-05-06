from models.Object import Object
from models.Category import Category
from flask import Blueprint, request, abort
from util.json import convert_to_json, returns_json
from models.base import get_session
from util.get_locale import validate_locale, get_locale


object_blueprint = Blueprint('objects', __name__)


@object_blueprint.route('/objects', methods=['GET'])
@returns_json
def get_objects():
    session = get_session()

    city_id = request.args.get('city')
    object_type = request.args.get('type')
    category = request.args.get('category')

    objects = session.query(Object).filter(
        Object.city_id == city_id if city_id is not None else True,
        Object.type == object_type if object_type is not None else True,
        Object.categories.any(Category.alias == category) if category is not None else True
    ).all()

    locale = get_locale()
    mapped_objects = list(map(lambda o: o.to_object_json(locale), objects))

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

    locale = get_locale()
    json_object = convert_to_json(obj, locale)

    session.close()

    return json_object
