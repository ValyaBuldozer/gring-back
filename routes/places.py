from uuid import uuid4

from flask import Blueprint, request, abort, g

from models.LocaleString import LocaleString
from util.get_locale import validate_locale, get_locale, get_post_locale
from util.json import returns_json, convert_to_json
from models.Place import Place
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.base import get_session
from flask_expects_json import expects_json
from util import osrm_client
import osrm
from util.decorators import roles_required
from models.RoleName import RoleName


place_blueptint = Blueprint('places', __name__)


@place_blueptint.route('/places', methods=['GET'])
@returns_json
def get_places():
    session = get_session()

    places = session.query(Place).all()

    locale = get_locale()
    json_places = convert_to_json(places, locale)

    session.close()

    return json_places


@place_blueptint.route('/places/<object_id>', methods=['GET'])
@returns_json
def get_place_by_id(object_id):
    session = get_session()

    place = session.query(Place).get(object_id)

    if place is None:
        session.close()
        abort(404, "Place with id = %s not found" % object_id)

    locale = get_locale()
    json_place = convert_to_json(place, locale)

    session.close()

    return json_place


put_place_schema = {
    'type': 'object',
    'properties': {
        'image_link': {'type': 'string'},
        'audioguide_link': {'type': 'string'},
        'description': {'type': 'string'},
        'city_id': {'type': 'integer'},
        'name': {'type': 'string'},
        'address': {'type': 'string'},
        'latitude': {'type': 'number', "minimum": -90, "maximum": 90},
        'longitude': {'type': 'number', "minimum": -180, "maximum": 180},
        'categories': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        }
    },
    'required': ['image_link', 'description', 'city_id', 'name', 'address', 'latitude',
                 'longitude', 'categories']
}


@place_blueptint.route('/places', methods=['PUT'])
@expects_json(put_place_schema)
@roles_required([RoleName.content_moder])
def put_new_place():
    session = get_session()
    content = g.data

    locale = get_post_locale(session)

    if session.query(City).get(content['city_id']) is None:
        session.close()
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    geolocation = Geolocation(
        latitude=content['latitude'],
        longitude=content['longitude']
    )

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    place = Place(
        image_link=content['image_link'],
        city_id=content['city_id'],
        geolocation=geolocation,
        categories=categories
    )

    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    place.name_id = name_id
    place.name.set(locale_string)

    description_id = str(uuid4())
    locale_string = LocaleString(
        id=description_id,
        locale=locale,
        text=content['description']
    )
    place.description_id = description_id
    place.description.set(locale_string)

    address_id = str(uuid4())
    locale_string = LocaleString(
        id=address_id,
        locale=locale,
        text=content['address']
    )
    place.address_id = address_id
    place.address.set(locale_string)

    audioguide_link_id = str(uuid4())
    locale_string = LocaleString(
        id=audioguide_link_id,
        locale=locale,
        text=content['audioguide_link']
    )
    place.audioguide_link_id = audioguide_link_id
    place.audioguide_link.set(locale_string)

    session.add(place)

    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['POST'])
@expects_json(put_place_schema)
@roles_required([RoleName.content_moder])
def post_place_by_id(object_id):
    session = get_session()
    place = session.query(Place).get(object_id)

    locale = get_post_locale(session)

    if place is None:
        session.close()
        abort(404, "Place with id = %s not found" % object_id)
        return

    content = g.data

    if session.query(City).get(content['city_id']) is None:
        session.close()
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    place.image_link = content['image_link']
    place.city_id = content['city_id']
    geolocation = session.query(Geolocation).get(place.geolocation_id)
    geolocation.latitude = content['latitude']
    geolocation.longitude = content['longitude']

    place.name.set(LocaleString(
        id=place.name_id,
        locale=locale,
        text=content['name']
    ))

    place.description.set(LocaleString(
        id=place.description_id,
        locale=locale,
        text=content['description']
    ))

    place.address.set(LocaleString(
        id=place.address_id,
        locale=locale,
        text=content['address']
    ))

    place.audioguide_link.set(LocaleString(
        id=place.audioguide_link_id,
        locale=locale,
        text=content['audioguide_link']
    ))

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    place.categories = categories

    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['DELETE'])
@roles_required([RoleName.content_moder])
def delete_place_by_id(object_id):
    session = get_session()
    place = session.query(Place).get(object_id)

    if place is None:
        session.close()
        abort(404, "Place with id = %s not found" % object_id)
        return

    session.delete(place)
    session.commit()
    session.close()

    return 'ok'


geolocation_schema = {
    'type': 'object',
    'properties': {
        'latitude': {'type': 'number', "minimum": -90, "maximum": 90},
        'longitude': {'type': 'number', "minimum": -180, "maximum": 180},
    },
    'required': ['latitude', 'longitude']
}


@place_blueptint.route('/places/distance/<object_id>', methods=['POST'])
@expects_json(geolocation_schema)
def get_distance_to_place(object_id):
    session = get_session()
    place = session.query(Place).get(object_id)

    if place is None:
        session.close()
        abort(404, "Place with id = %s not found" % object_id)
        return

    content = g.data

    user_geo_point = [content['longitude'], content['latitude']]
    place_geo_point = [place.geolocation.longitude, place.geolocation.latitude]

    session.close()

    geo_points = [user_geo_point, place_geo_point]

    response = osrm_client.client.route(
        coordinates=geo_points,
        overview=osrm.overview.full)

    if 'routes' in response:
        return str(response['routes'][0]['distance'])
    else:
        abort(500, "Internal Error: Can't get valid response from OSRM service.")



