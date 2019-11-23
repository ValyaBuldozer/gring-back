from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.Place import Place
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.CategoryObject import CategoryObject
from models.base import get_session
from flask_expects_json import expects_json


place_blueptint = Blueprint('places', __name__)


@place_blueptint.route('/places', methods=['GET'])
@returns_json
def get_places():
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
        'latitude': {'type': 'number'},
        'longtude': {'type': 'number'},
        'category_id': {'type': 'integer'}
    },
    'required': ['description', 'city_id', 'name', 'address', 'latitude',
                 'longtude', 'category_id']
}


@place_blueptint.route('/places', methods=['PUT'])
@expects_json(put_place_schema)
@returns_json
def put_new_place():
    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, 'City with such id not found')
        return

    if Category.query.get(content['category_id']) is None:
        abort(400, 'Category with such id not found')
        return

    session = get_session()
    geolocation = Geolocation(
        latitude=content['latitude'],
        longtude=content['longtude']
    )

    session.add(geolocation)
    session.flush()

    place = Place(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        address=content['address'],
        geolocation_id=geolocation.id
    )

    session.add(place)
    session.flush()

    category_object = CategoryObject.insert().values(
        object_id=place.id,
        category_id=content['category_id'])

    session.execute(category_object)
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
        abort(400, 'City with such id not found')
        return

    if Category.query.get(content['category_id']) is None:
        abort(400, 'Category with such id not found')
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
    # забивается
    # чекать в бд: show processlist;
    category_object = CategoryObject.update(). \
        where(CategoryObject.c.object_id == object_id).values(category_id=content['category_id'])

    session.execute(category_object)
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

    geolocation = session.query(Geolocation).get(place.geolocation_id)
    # забивается
    # чекать в бд: show processlist;
    category_object = CategoryObject.delete().where(
        CategoryObject.c.object_id == object_id)

    session.delete(place)
    session.delete(geolocation)
    session.execute(category_object)
    session.commit()
    session.close()

    return 'ok'
