from uuid import uuid4

from flask import Blueprint, request, abort, g

from models.LocaleString import LocaleString
from util.get_locale import get_locale
from util.json import returns_json, convert_to_json, validate_locale
from models.PublicPlace import PublicPlace
from models.City import City
from models.Geolocation import Geolocation
from models.Category import Category
from models.Timetable import Timetable
from models.WeekDay import WeekDay
from models.base import get_session
from flask_expects_json import expects_json
from util.decorators import roles_required
from models.RoleName import RoleName


public_place_blueptint = Blueprint('public_places', __name__)


@public_place_blueptint.route('/public_places', methods=['GET'])
@returns_json
def get_public_places():
    session = get_session()

    public_places = session.query(PublicPlace).all()

    locale = get_locale()
    json_public_places = convert_to_json(public_places, locale)

    session.close()

    return json_public_places


@public_place_blueptint.route('/public_places/<object_id>', methods=['GET'])
@returns_json
def get_public_places_by_id(object_id):
    session = get_session()

    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        session.close()
        abort(404, "Public place with id = %s not found" % object_id)

    locale = get_locale()
    json_public_place = convert_to_json(public_place, locale)

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
        'longitude': {'type': 'number', "minimum": -180, "maximum": 180},
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
                 'longitude', 'categories', 'timetable']
}


@public_place_blueptint.route('/public_places', methods=['PUT'])
@expects_json(put_public_place_schema)
@roles_required([RoleName.content_moder])
def put_new_public_place():
    session = get_session()
    content = g.data

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

    timetable = []

    for timetable_item in content['timetable']:
        timetable.append(Timetable(
            week_day=WeekDay(timetable_item['day']),
            open_time=timetable_item['open_time'],
            close_time=timetable_item['close_time'],
        ))

    public_place = PublicPlace(
        image_link=content['image_link'],
        city_id=content['city_id'],
        geolocation=geolocation,
        categories=categories,
        timetable=timetable
    )

    locale = validate_locale(request.headers.get('locale'))

    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    public_place.name_id = name_id
    public_place.name.set(locale_string)

    description_id = str(uuid4())
    locale_string = LocaleString(
        id=description_id,
        locale=locale,
        text=content['description']
    )
    public_place.description_id = description_id
    public_place.description.set(locale_string)

    address_id = str(uuid4())
    locale_string = LocaleString(
        id=address_id,
        locale=locale,
        text=content['address']
    )
    public_place.address_id = address_id
    public_place.address.set(locale_string)

    audioguide_link_id = str(uuid4())
    locale_string = LocaleString(
        id=audioguide_link_id,
        locale=locale,
        text=content['audioguide_link']
    )
    public_place.audioguide_link_id = audioguide_link_id
    public_place.audioguide_link.set(locale_string)

    session.add(public_place)

    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['POST'])
@expects_json(put_public_place_schema)
@roles_required([RoleName.content_moder])
def post_public_place_by_id(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        session.close()
        abort(404, "Public place with id = %s not found" % object_id)
        return

    content = g.data

    if session.query(City).get(content['city_id']) is None:
        session.close()
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    public_place.image_link = content['image_link']
    public_place.city_id = content['city_id']
    geolocation = session.query(Geolocation).get(public_place.geolocation_id)
    geolocation.latitude = content['latitude']
    geolocation.longitude = content['longitude']

    locale = validate_locale(request.headers.get('locale'))

    public_place.name.set(LocaleString(
        id=public_place.name_id,
        locale=locale,
        text=content['name']
    ))

    public_place.description.set(LocaleString(
        id=public_place.description_id,
        locale=locale,
        text=content['description']
    ))

    public_place.address.set(LocaleString(
        id=public_place.address_id,
        locale=locale,
        text=content['address']
    ))

    public_place.audioguide_link.set(LocaleString(
        id=public_place.audioguide_link_id,
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
@roles_required([RoleName.content_moder])
def delete_public_place_by_id(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        session.close()
        abort(404, "Public place with id = %s not found" % object_id)
        return

    session.delete(public_place)

    session.commit()
    session.close()

    return 'ok'



