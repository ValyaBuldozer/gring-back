from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.Place import Place
from models.Object import Object
from models.City import City
from models.Geolocation import Geolocation
from models.base import get_session
from flask_expects_json import expects_json


place_blueptint = Blueprint('places', __name__)


@place_blueptint.route('/places', methods=['GET'])
@returns_json
def get_reviews():
    places = Place.query.all()

    return to_json(places)


put_place_schema = {
    'type': 'object',
    'properties': {
        'image_link': {'type': 'string'},
        'audioguide_link': {'type': 'string'},
        'description': {'type': 'string'},
        'city_id': {'type': 'integer'},
        'name': {'type': 'string'},
        'address': {'type': 'string'},
        'geolocation_id': {'type': 'integer'}
    },
    'required': ['description', 'city_id', 'name', 'address', 'geolocation_id']
}


@place_blueptint.route('/places', methods=['PUT'])
@expects_json(put_place_schema)
@returns_json
def put_new_place():
    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(404, 'City not found')
        return

    if Geolocation.query.get(content['geolocation_id']) is None:
        abort(404, 'Geolocation not found')
        return

    session = get_session()
    place = Place(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        address=content['address'],
        geolocation_id=content['geolocation_id']
    )

    session.add(place)
    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['POST'])
@expects_json(put_place_schema)
@returns_json
def post_place(object_id):
    if Place.query.get(object_id) is None:
        abort(404, 'Place not found')
        return

    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(404, 'City not found')
        return

    if Geolocation.query.get(content['geolocation_id']) is None:
        abort(404, 'Geolocation not found')
        return

    session = get_session()
    place = session.query(Place).get(object_id)
    place.image_link = content['image_link']
    place.audioguide_link = content['audioguide_link']
    place.description = content['description']
    place.city_id = content['city_id']
    place.name = content['name']
    place.address = content['address']
    place.geolocation_id = content['geolocation_id']

    session.commit()
    session.close()

    return 'ok'


@place_blueptint.route('/places/<object_id>', methods=['DELETE'])
@returns_json
def delete_place(object_id):
    session = get_session()
    place = session.query(Place).get(object_id)

    if place is None:
        abort(404, 'Place not found')
        return

    session.delete(place)
    session.commit()
    session.close()

    return 'ok'
