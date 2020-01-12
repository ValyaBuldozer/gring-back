from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.Place import Place
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.base import get_session
from flask_expects_json import expects_json


place_blueptint = Blueprint('places', __name__)


@place_blueptint.route('/places', methods=['GET'])
@returns_json
def get_places():
    session = get_session()

    places = session.query(Place).all()

    json_places = to_json(places)

    session.close()

    return json_places


@place_blueptint.route('/places/<object_id>', methods=['GET'])
@returns_json
def get_place_by_id(object_id):
    session = get_session()

    place = session.query(Place).get(object_id)

    if place is None:
        abort(404, "Place with id = %s not found" % object_id)

    json_place = to_json(place)

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
        'longtude': {'type': 'number', "minimum": -180, "maximum": 180},
        'categories': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        }
    },
    'required': ['image_link', 'description', 'city_id', 'name', 'address', 'latitude',
                 'longtude', 'categories']
}


@place_blueptint.route('/places/', methods=['PUT'])
@expects_json(put_place_schema)
@returns_json
def put_new_place():
    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    session = get_session()
    geolocation = Geolocation(
        latitude=content['latitude'],
        longtude=content['longtude']
    )

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.rollback()
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    place = Place(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        address=content['address'],
        geolocation=geolocation,
        categories=categories
    )

    session.add(place)

    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['POST'])
@expects_json(put_place_schema)
@returns_json
def post_place_by_id(object_id):
    if Place.query.get(object_id) is None:
        abort(404, "Place with id = %s not found" % object_id)
        return

    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    session = get_session()
    place = session.query(Place).get(object_id)
    place.image_link = content['image_link']
    place.audioguide_link = content['audioguide_link']
    place.description = content['description']
    place.city_id = content['city_id']
    place.name = content['name']
    place.address = content['address']
    geolocation = session.query(Geolocation).get(place.geolocation_id)
    geolocation.latitude = content['latitude']
    geolocation.longtude = content['longtude']

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.rollback()
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    place.categories = categories

    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['DELETE'])
@returns_json
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
