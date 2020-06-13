from uuid import uuid4

from flask import Blueprint, request, abort, g

from models.Language import Language
from models.LocaleLink import LocaleLink
from models.LocaleString import LocaleString
from util.audio_service import delete_audio
from util.get_locale import validate_locale, get_locale, get_post_locale
from util.image_service import delete_image
from util.json import returns_json, convert_to_json
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
        },
        'phone_number': {'type': 'string'},
        'site': {'type': 'string'},
        'avg_bill': {'type': 'string'},
        'visit_cost': {'type': 'string'}
    },
    'required': ['image_link', 'description', 'city_id', 'name', 'address', 'latitude',
                 'longitude', 'categories', 'timetable']
}


@public_place_blueptint.route('/public_places', methods=['PUT'])
@expects_json(put_public_place_schema)
@roles_required([RoleName.admin, RoleName.content_moder])
def put_new_public_place():
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

    if 'phone_number' in content:
        public_place.phone_number = content['phone_number']

    if 'site' in content:
        public_place.site = content['site']

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

    if 'audioguide_link' in content:
        audioguide_link_id = str(uuid4())
        locale_link = LocaleLink(
            id=audioguide_link_id,
            locale=locale,
            path=content['audioguide_link']
        )
        public_place.audioguide_link_id = audioguide_link_id
        public_place.audioguide_link.set(locale_link)

    if 'avg_bill' in content:
        avg_bill_id = str(uuid4())
        locale_string = LocaleString(
            id=avg_bill_id,
            locale=locale,
            text=content['avg_bill']
        )
        public_place.avg_bill_id = avg_bill_id
        public_place.avg_bill.set(locale_string)

    if 'visit_cost' in content:
        visit_cost_id = str(uuid4())
        locale_string = LocaleString(
            id=visit_cost_id,
            locale=locale,
            text=content['visit_cost']
        )
        public_place.visit_cost_id = visit_cost_id
        public_place.visit_cost.set(locale_string)

    session.add(public_place)

    session.commit()
    session.close()

    return 'ok'


@public_place_blueptint.route('/public_places/<object_id>', methods=['POST'])
@expects_json(put_public_place_schema)
@roles_required([RoleName.admin, RoleName.content_moder])
def post_public_place_by_id(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    locale = get_post_locale(session)

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
    public_place.phone_number = content['phone_number'],
    public_place.site = content['site'],
    geolocation = session.query(Geolocation).get(public_place.geolocation_id)
    geolocation.latitude = content['latitude']
    geolocation.longitude = content['longitude']

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

    if 'audioguide_link' in content:
        if public_place.audioguide_link_id is not None:
            public_place.audioguide_link.set(LocaleLink(
                id=public_place.audioguide_link_id,
                locale=locale,
                path=content['audioguide_link']
            ))
        else:
            audioguide_link_id = str(uuid4())
            locale_link = LocaleLink(
                id=audioguide_link_id,
                locale=locale,
                path=content['audioguide_link']
            )
            public_place.audioguide_link_id = audioguide_link_id
            public_place.audioguide_link.set(locale_link)
    else:
        if public_place.audioguide_link_id is not None:
            locale_link = session.query(LocaleLink).filter(
                LocaleLink.id == public_place.audioguide_link_id,
                LocaleLink.locale == locale
            ).first()
            session.delete(locale_link)

    if 'avg_bill' in content:
        if public_place.avg_bill_id is not None:
            public_place.avg_bill.set(LocaleString(
                id=public_place.avg_bill_id,
                locale=locale,
                text=content['avg_bill']
            ))
        else:
            avg_bill_id = str(uuid4())
            locale_string = LocaleString(
                id=avg_bill_id,
                locale=locale,
                text=content['avg_bill']
            )
            public_place.avg_bill_id = avg_bill_id
            public_place.avg_bill.set(locale_string)
    else:
        if public_place.avg_bill_id is not None:
            locale_string = session.query(LocaleString).filter(
                LocaleString.id == public_place.avg_bill_id,
                LocaleString.locale == locale
            ).first()
            session.delete(locale_string)

    if 'visit_cost' in content:
        if public_place.visit_cost_id is not None:
            public_place.visit_cost.set(LocaleString(
                id=public_place.visit_cost_id,
                locale=locale,
                text=content['visit_cost']
            ))
        else:
            visit_cost_id = str(uuid4())
            locale_string = LocaleString(
                id=visit_cost_id,
                locale=locale,
                text=content['visit_cost']
            )
            public_place.visit_cost_id = visit_cost_id
            public_place.visit_cost.set(locale_string)
    else:
        if public_place.visit_cost_id is not None:
            locale_string = session.query(LocaleString).filter(
                LocaleString.id == public_place.visit_cost_id,
                LocaleString.locale == locale
            ).first()
            session.delete(locale_string)

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
@roles_required([RoleName.admin, RoleName.content_moder])
def delete_public_place_by_id(object_id):
    session = get_session()
    public_place = session.query(PublicPlace).get(object_id)

    if public_place is None:
        session.close()
        abort(404, "Public place with id = %s not found" % object_id)
        return

    if public_place.image_link is not None:
        delete_image(public_place.image_link)

    for lang in Language.__members__:
        audio = public_place.audioguide_link.get(lang)
        if audio is not None:
            delete_audio(audio)

    session.delete(public_place)

    session.commit()
    session.close()

    return 'ok'
