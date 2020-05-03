from flask_expects_json import expects_json
from models.Category import Category
from models.CategoryObject import CategoryObject
from flask import Blueprint, request, abort, g
from models.LocaleString import LocaleString
from models.RoleName import RoleName
from util.decorators import roles_required
from util.get_locale import get_locale
from util.json import convert_to_json, returns_json, validate_locale
from models.base import get_session
from sqlalchemy import desc
from sqlalchemy import func
from uuid import uuid4


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

    locale = get_locale()
    json_categories = convert_to_json(categories, locale)

    session.close()

    return json_categories


@category_blueprint.route('/categories/<category_id>', methods=['GET'])
@returns_json
def get_category_by_id(category_id):
    session = get_session()

    cat = session.query(Category).get(category_id)

    if cat is None:
        session.close()
        abort(404, "Category with id = %s not found" % category_id)

    locale = get_locale()
    json_category = convert_to_json(cat, locale)

    session.close()

    return json_category


put_category_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
    },
    'required': ['name']
}


@category_blueprint.route('/categories', methods=['PUT'])
@expects_json(put_category_schema)
def put_new_category():
    session = get_session()
    content = g.data

    locale = validate_locale(request.headers.get('locale'))

    category = Category()
    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    category.name_id = name_id
    category.name.set(locale_string)

    session.add(category)

    session.commit()
    session.close()

    return 'ok'


@category_blueprint.route('/categories/<category_id>', methods=['POST'])
@expects_json(put_category_schema)
def post_category_by_id(category_id):
    session = get_session()
    category = session.query(Category).get(category_id)

    if category is None:
        session.close()
        abort(404, "Category with id = %s not found" % category_id)
        return

    content = g.data
    locale = validate_locale(request.headers.get('locale'))

    category.name.set(LocaleString(
        id=category.name_id,
        locale=locale,
        text=content['name']
    ))

    session.commit()
    session.close()

    return 'ok'


@category_blueprint.route('/categories/<category_id>', methods=['DELETE'])
@roles_required([RoleName.content_moder])
def delete_place_by_id(category_id):
    session = get_session()
    category = session.query(Category).get(category_id)

    if category is None:
        session.close()
        abort(404, "Category with id = %s not found" % category_id)
        return

    session.delete(category)
    session.commit()
    session.close()

    return 'ok'
