from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.PublicPlace import PublicPlace
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.CategoryObject import CategoryObject
from models.Timetable import Timetable
from models.WeekDay import WeekDay
from models.base import get_session
from flask_expects_json import expects_json


public_place_blueptint = Blueprint('public_places', __name__)


@public_place_blueptint.route('/public_places', methods=['GET'])
@returns_json
def get_public_places():
    public_places = PublicPlace.query.all()

    return to_json(public_places)


put_public_place_schema = {
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
        'category_id': {'type': 'integer'},
        'timetable': {
            'type': 'array',
            'items': {
                'day': {
                    "type": "string",
                    "enum": [WeekDay.mon, WeekDay.tue, WeekDay.wed, WeekDay.thu, WeekDay.fri,
                             WeekDay.sat, WeekDay.sun]
                },
                'open_time': {'type': 'string'},
                'close_time': {'type': 'string'}
            },
            'required': ['day', 'open_time', 'close_time']
        }
    },
    'required': ['description', 'city_id', 'name', 'address', 'latitude',
                 'longtude', 'category_id', 'timetable']
}


@public_place_blueptint.route('/public_places', methods=['PUT'])
@expects_json(put_public_place_schema)
@returns_json
def put_new_public_place():
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

    public_place = PublicPlace(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        address=content['address'],
        geolocation_id=geolocation.id,
    )

    session.add(public_place)
    session.flush()

    category_object = CategoryObject.insert().values(
        object_id=public_place.id,
        category_id=content['category_id'])

    session.execute(category_object)

    for timetable_item in content['timetable']:
        timetable = Timetable(
            id=public_place.id,
            week_day=WeekDay(timetable_item['day']),
            open_time=timetable_item['open_time'],
            close_time=timetable_item['close_time'],
        )
        session.add(timetable)

    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['POST'])
@expects_json(put_public_place_schema)
@returns_json
def post_place(object_id):
    if PublicPlace.query.get(object_id) is None:
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
    # забивается
    # чекать в бд: show processlist;
    category_object = CategoryObject.update(). \
        where(CategoryObject.c.object_id == object_id).values(category_id=content['category_id'])

    session.execute(category_object)

    # 1 или 2
    # 1
    # timetable_items = []
    for timetable_item in content['timetable']:
        timetable = session.query(Timetable).filter(Timetable.id == public_place.id). \
            filter(Timetable.week_day == WeekDay(timetable_item['day']))
        timetable.week_day = WeekDay(timetable_item['day'])
        timetable.week_day = timetable_item['open_time']
        timetable.week_day = timetable_item['close_time']
        # 1
        # timetable_items.append(timetable)
        # 2
        # session.add(timetable)
        # session.flush()

    # 1
    # session.add(timetable_items)
    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['DELETE'])
@returns_json
def delete_public_place(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        abort(404, 'Public_place not found')
        return

    geolocation = session.query(Geolocation).get(public_place.geolocation_id)
    # забивается
    # чекать в бд: show processlist;
    category_object = CategoryObject.delete().where(
        CategoryObject.c.object_id == object_id)

    session.execute(category_object)

    for timetable_item in session.query(Timetable).filter(Timetable.id == public_place.id):
        session.delete(timetable_item)

    session.delete(public_place)
    session.delete(geolocation)
    session.commit()
    session.close()

    return 'ok'



