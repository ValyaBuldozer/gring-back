from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.PublicPlace import PublicPlace
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.Timetable import Timetable
from models.WeekDay import WeekDay
from models.base import get_session
from flask_expects_json import expects_json


public_place_blueptint = Blueprint('public_places', __name__)


@public_place_blueptint.route('/public_places', methods=['GET'])
@returns_json
def get_public_places():
    session = get_session()

    public_places = session.query(PublicPlace).all()

    json_public_places = to_json(public_places)

    session.close()

    return json_public_places


@public_place_blueptint.route('/public_places/<object_id>', methods=['GET'])
@returns_json
def get_public_places_by_id(object_id):
    session = get_session()

    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        abort(400, "Public place with id = %s not found" % object_id)

    json_public_place = to_json(public_place)

    session.close()

    return json_public_place


put_public_place_schema = {
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
        },
        'timetable': {
            'type': 'array',
            'items': {
                'day': {
                    'type': 'string',
                    'enum': [e.name for e in WeekDay]
                },
                'open_time': {
                    'type': 'string',
                    'format': 'time'
                },
                'close_time': {
                    'type': 'string',
                    'format': 'time'
                }
            },
            'required': ['day', 'open_time', 'close_time']
        }
    },
    'required': ['image_link', 'description', 'city_id', 'name', 'address', 'latitude',
                 'longtude', 'categories', 'timetable']
}


@public_place_blueptint.route('/public_places/', methods=['PUT'])
@expects_json(put_public_place_schema)
@returns_json
def put_new_public_place():
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

    timetable = []

    for timetable_item in content['timetable']:
        timetable.append(Timetable(
            week_day=WeekDay(timetable_item['day']),
            open_time=timetable_item['open_time'],
            close_time=timetable_item['close_time'],
        ))

    public_place = PublicPlace(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        address=content['address'],
        geolocation=geolocation,
        categories=categories,
        timetable=timetable
    )

    session.add(public_place)

    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['POST'])
@expects_json(put_public_place_schema)
@returns_json
def post_public_place_by_id(object_id):
    if PublicPlace.query.get(object_id) is None:
        abort(400, "Public place with id = %s not found" % object_id)
        return

    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)
    public_place.image_link = content['image_link']
    public_place.audioguide_link = content['audioguide_link']
    public_place.description = content['description']
    public_place.city_id = content['city_id']
    public_place.name = content['name']
    public_place.address = content['address']
    geolocation = session.query(Geolocation).get(public_place.geolocation_id)
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

    public_place.categories = categories

    timetable = []

    for timetable_item in content['timetable']:
        timetable.append(Timetable(
            week_day=WeekDay(timetable_item['day']),
            open_time=timetable_item['open_time'],
            close_time=timetable_item['close_time'],
        ))

    public_place.timetable = timetable

    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['DELETE'])
@returns_json
def delete_public_place_by_id(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        session.close()
        abort(400, "Public place with id = %s not found" % object_id)
        return

    session.delete(public_place)

    session.commit()
    session.close()

    return 'ok'



