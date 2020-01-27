from models.Category import Category
from models.CategoryObject import CategoryObject
from flask import Blueprint, request, abort
from util.json import to_json, returns_json
from models.base import get_session
from sqlalchemy import desc
from sqlalchemy import func


category_blueprint = Blueprint('categories', __name__)


@category_blueprint.route('/categories', methods=['GET'])
@returns_json
def get_categories():
    session = get_session()

    categories = session.query(Category)\
        .outerjoin(CategoryObject)\
        .group_by(Category)\
        .order_by(desc(func.count(CategoryObject.c.object_id)))\
        .all()

    json_categories = to_json(categories)

    session.close()

    return json_categories


@category_blueprint.route('/categories/<category_id>', methods=['GET'])
@returns_json
def get_category_by_id(category_id):
    session = get_session()

    cat = session.query(Category).get(category_id)

    if cat is None:
        abort(404, "Category with id = %s not found" % category_id)

    json_category = to_json(cat)

    session.close()

    return json_category
