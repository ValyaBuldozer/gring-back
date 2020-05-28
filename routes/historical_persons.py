from uuid import uuid4

from flask import Blueprint, request, abort, g

from models.Language import Language
from models.LocaleString import LocaleString
from util.audio_service import delete_audio
from util.get_locale import validate_locale, get_locale, get_post_locale
from util.image_service import delete_image
from util.json import returns_json, convert_to_json
from models.HistoricalPerson import HistoricalPerson
from models.City import City
from models.Object import Object
from models.Category import Category
from models.base import get_session
from flask_expects_json import expects_json
from util.decorators import roles_required
from models.RoleName import RoleName


historical_person_blueptint = Blueprint('historical_persons', __name__)


@historical_person_blueptint.route('/historical_persons', methods=['GET'])
@returns_json
def get_historical_persons():
    session = get_session()

    historical_persons = session.query(HistoricalPerson).all()

    locale = get_locale()
    json_historical_persons = convert_to_json(historical_persons, locale)

    session.close()

    return json_historical_persons


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['GET'])
@returns_json
def get_historical_person_by_id(object_id):
    session = get_session()

    historical_person = session.query(HistoricalPerson).get(object_id)

    if historical_person is None:
        session.close()
        abort(404, "Historical person with id = %s not found" % object_id)

    locale = get_locale()
    json_historical_person = convert_to_json(historical_person, locale)

    session.close()

    return json_historical_person


put_historical_person_schema = {
    'type': 'object',
    'properties': {
        'image_link': {'type': 'string'},
        'audioguide_link': {'type': 'string'},
        'description': {'type': 'string'},
        'city_id': {'type': 'integer'},
        'name': {'type': 'string'},
        'second_name': {'type': 'string'},
        'patronymic': {'type': 'string'},
        'birthdate': {
            'type': 'string',
            'format': 'date'
        },
        'deathdate': {
            'type': 'string',
            'format': 'date'
        },
        'categories': {
            'type': 'array',
            'item': {'type': 'integer'},
            "minItems": 1
        },
        'related_objects': {
            'type': 'array',
            'item': {'type': 'integer'}
        },
    },
    'required': ['image_link', 'description', 'city_id', 'name', 'second_name', 'birthdate', 'categories',
                 'related_objects']
}


@historical_person_blueptint.route('/historical_persons', methods=['PUT'])
@expects_json(put_historical_person_schema)
@roles_required([RoleName.content_moder])
def put_new_hisrorical_person():
    content = g.data
    session = get_session()

    locale = get_post_locale(session)

    if session.query(City).get(content['city_id']) is None:
        session.close()
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    related_objects = []

    for object_id in content['related_objects']:
        obj = session.query(Object).get(object_id)

        if obj is None:
            session.close()
            abort(400, "Related object with id = %s not found" % object_id)
            return

        related_objects.append(obj)

    historical_person = HistoricalPerson(
        image_link=content['image_link'],
        city_id=content['city_id'],
        birthdate=content['birthdate'],
        deathdate=content['deathdate'],
        categories=categories,
        related_objects=related_objects,
    )

    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    historical_person.name_id = name_id
    historical_person.name.set(locale_string)

    second_name_id = str(uuid4())
    locale_string = LocaleString(
        id=second_name_id,
        locale=locale,
        text=content['second_name']
    )
    historical_person.second_name_id = second_name_id
    historical_person.second_name.set(locale_string)

    patronymic_id = str(uuid4())
    locale_string = LocaleString(
        id=patronymic_id,
        locale=locale,
        text=content['patronymic']
    )
    historical_person.patronymic_id = patronymic_id
    historical_person.patronymic.set(locale_string)

    description_id = str(uuid4())
    locale_string = LocaleString(
        id=description_id,
        locale=locale,
        text=content['description']
    )
    historical_person.description_id = description_id
    historical_person.description.set(locale_string)

    audioguide_link_id = str(uuid4())
    locale_string = LocaleString(
        id=audioguide_link_id,
        locale=locale,
        text=content['audioguide_link']
    )
    historical_person.audioguide_link_id = audioguide_link_id
    historical_person.audioguide_link.set(locale_string)

    session.add(historical_person)

    session.commit()
    session.close()

    return 'ok'


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['POST'])
@expects_json(put_historical_person_schema)
@roles_required([RoleName.content_moder])
def post_hisrorical_person_by_id(object_id):
    session = get_session()
    content = g.data

    locale = get_post_locale(session)

    historical_person = session.query(HistoricalPerson).get(object_id)
    if historical_person is None:
        session.close()
        abort(404, "Historical person with id = %s not found" % object_id)
        return

    if session.query(City).get(content['city_id']) is None:
        session.close()
        abort(400, "City with id = %s not found" % content['city_id'])
        return

    historical_person.image_link = content['image_link']
    historical_person.audioguide_link = content['audioguide_link']
    historical_person.city_id = content['city_id']
    historical_person.birthdate = content['birthdate']
    historical_person.deathdate = content['deathdate']

    historical_person.name.set(LocaleString(
        id=historical_person.name_id,
        locale=locale,
        text=content['name']
    ))

    historical_person.second_name.set(LocaleString(
        id=historical_person.second_name_id,
        locale=locale,
        text=content['second_name']
    ))

    if 'patronymic' in content:
        historical_person.patronymic.set(LocaleString(
            id=historical_person.patronymic_id,
            locale=locale,
            text=content['patronymic']
        ))

    historical_person.audioguide_link.set(LocaleString(
        id=historical_person.audioguide_link_id,
        locale=locale,
        text=content['audioguide_link']
    ))

    historical_person.description.set(LocaleString(
        id=historical_person.description_id,
        locale=locale,
        text=content['description']
    ))

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.close()
            abort(400, "Category with id = %s not found" % category_id)
            return

        categories.append(category)

    historical_person.categories = categories

    related_objects = []

    for object_id in content['related_objects']:
        obj = session.query(Object).get(object_id)

        if obj is None:
            session.close()
            abort(400, "Related object with id = %s not found" % object_id)
            return

        related_objects.append(obj)

    historical_person.related_objects = related_objects

    session.commit()
    session.close()

    return 'ok'


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['DELETE'])
def delete_historical_person_by_id(object_id):
    session = get_session()
    historical_person = session.query(HistoricalPerson).get(object_id)

    if historical_person is None:
        session.close()
        abort(404, "'Historical person with id = %s not found" % object_id)
        return

    if historical_person.image_link is not None:
        delete_image(historical_person.image_link)

    for lang in Language.__members__:
        audio = historical_person.audioguide_link.get(lang)
        if audio is not None:
            delete_audio(audio)

    session.delete(historical_person)

    session.commit()
    session.close()

    return 'ok'

