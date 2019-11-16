from models.Object import Object
from models.Category import Category
from flask import Blueprint, request, abort
from helpers.json import to_json
from helpers.array import contains

object_routes = Blueprint('objects', __name__)


@object_routes.route('/objects', methods=['GET'])
def get_objects():
    object_type = request.args.get('type')
    category = request.args.get('category')
    objects = Object.query.filter(
        Object.type == object_type if 'type' in request.args else True,
        Object.categories.any(Category.name == category) if 'category' in request.args else True
    ).all()

    return to_json(objects)


@object_routes.route('/objects/<object_id>', methods=['GET'])
def get_object_by_id(object_id):
    if Object.query.filter(Object.id == object_id).count() > 0:
        return to_json(Object.query.get(object_id))
    else:
        abort(404, 'Object not found')
