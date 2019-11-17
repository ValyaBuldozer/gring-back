from models.Object import Object
from models.Category import Category
from flask import Blueprint, request, abort
from util.json import to_json, returns_json

object_blueprint = Blueprint('objects', __name__)


@object_blueprint.route('/objects', methods=['GET'])
@returns_json
def get_objects():
    object_type = request.args.get('type')
    category = request.args.get('category')
    objects = Object.query.filter(
        Object.type == object_type if 'type' in request.args else True,
        Object.categories.any(Category.name == category) if 'category' in request.args else True
    ).all()

    return to_json(list(map(lambda o: o.to_base_json(), objects)))


@object_blueprint.route('/objects/<object_id>', methods=['GET'])
@returns_json
def get_object_by_id(object_id):

    obj = Object.query.get(object_id)

    if (obj is None):
        abort(404, 'Object not found')

    return to_json(obj)
