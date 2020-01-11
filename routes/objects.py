from models.Object import Object
from models.Category import Category
from flask import Blueprint, request, abort
from util.json import to_json, returns_json
from models.base import get_session


object_blueprint = Blueprint('objects', __name__)


@object_blueprint.route('/objects', methods=['GET'])
@returns_json
def get_objects():
    session = get_session()

    object_type = request.args.get('type')
    category = request.args.get('category')
    objects = session.query(Object).filter(
        Object.type == object_type if 'type' in request.args else True,
        Object.categories.any(Category.name == category) if 'category' in request.args else True
    ).all()

    json_objects = to_json(list(map(lambda o: o.to_base_json(), objects)))

    session.close()

    return json_objects


@object_blueprint.route('/objects/<object_id>', methods=['GET'])
@returns_json
def get_object_by_id(object_id):
    session = get_session()

    obj = session.query(Object).get(object_id)

    if obj is None:
        abort(400, "Object with id = %s not found" % object_id)

    json_object = to_json(obj)

    session.close()

    return json_object
