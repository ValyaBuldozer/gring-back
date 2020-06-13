from flask_expects_json import expects_json

from models.City import City
from flask import Blueprint, request, abort, g
from models.LocaleString import LocaleString
from models.RoleName import RoleName
from util.decorators import roles_required
from util.get_locale import validate_locale, get_locale, get_post_locale
from util.json import convert_to_json, returns_json
from models.base import get_session
from uuid import uuid4


city_blueprint = Blueprint('cities', __name__)


@city_blueprint.route('/cities', methods=['GET'])
@returns_json
def get_cities():
    session = get_session()

    cities = session.query(City).all()

    locale = get_locale()
    json_cities = convert_to_json(cities, locale)

    session.close()

    return json_cities


@city_blueprint.route('/cities/<city_id>', methods=['GET'])
@returns_json
def get_city_by_id(city_id):
    session = get_session()

    city = session.query(City).get(city_id)

    if city is None:
        session.close()
        abort(404, "City with id = %s not found" % city_id)

    locale = get_locale()
    json_city = convert_to_json(city, locale)

    session.close()

    return json_city


put_city_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'image_link': {'type': 'string'},
        'description': {'type': 'string'}
    },
    'required': ['name']
}


@city_blueprint.route('/cities', methods=['PUT'])
@expects_json(put_city_schema)
def put_new_city():
    session = get_session()
    content = g.data

    locale = get_post_locale(session)

    city = City()
    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    city.name_id = name_id
    city.name.set(locale_string)

    description_id = str(uuid4())
    locale_string = LocaleString(
        id=description_id,
        locale=locale,
        text=content['description']
    )
    city.description_id = name_id
    city.description.set(locale_string)

    city.image_link = content['image_link']

    session.add(city)

    session.commit()
    session.close()

    return 'ok'


@city_blueprint.route('/cities/<city_id>', methods=['POST'])
@expects_json(put_city_schema)
def post_city_by_id(city_id):
    session = get_session()
    city = session.query(City).get(city_id)

    locale = get_post_locale(session)

    if city is None:
        session.close()
        abort(404, "City with id = %s not found" % city_id)
        return

    content = g.data

    city.name.set(LocaleString(
        id=city.name_id,
        locale=locale,
        text=content['name']
    ))

    city.description.set(LocaleString(
        id=city.description_id,
        locale=locale,
        text=content['description']
    ))

    city.image_link = content['image_link']

    session.commit()
    session.close()

    return 'ok'


@city_blueprint.route('/cities/<city_id>', methods=['DELETE'])
@roles_required([RoleName.admin, RoleName.content_moder])
def delete_city_by_id(city_id):
    session = get_session()
    city = session.query(City).get(city_id)

    if city is None:
        session.close()
        abort(404, "City with id = %s not found" % city_id)
        return

    session.delete(city)
    session.commit()
    session.close()

    return 'ok'
