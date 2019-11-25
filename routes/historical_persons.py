from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.HistoricalPerson import HistoricalPerson
from models.City import City
from models.Object import Object
from models.Category import Category
from models.base import get_session
from flask_expects_json import expects_json


historical_person_blueptint = Blueprint('historical_persons', __name__)


@historical_person_blueptint.route('/historical_persons', methods=['GET'])
@returns_json
def get_historical_persons():
    historical_persons = HistoricalPerson.query.all()

    return to_json(historical_persons)


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['GET'])
@returns_json
def get_historical_person_by_id(object_id):
    historical_person = HistoricalPerson.query.get(object_id)

    if historical_person is None:
        abort(404, 'Historical person not found')

    return to_json(historical_person)


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


@historical_person_blueptint.route('/historical_persons/', methods=['PUT'])
@expects_json(put_historical_person_schema)
@returns_json
def put_new_hisrorical_person():
    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, 'City with such id not found')
        return

    session = get_session()

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.rollback()
            session.close()
            abort(400, 'Category not found')
            return

        categories.append(category)

    related_objects = []

    for object_id in content['related_objects']:
        object = session.query(Object).get(object_id)

        if object is None:
            session.rollback()
            session.close()
            abort(400, 'Related object not found')
            return

        related_objects.append(object)

    historical_person = HistoricalPerson(
        image_link=content['image_link'],
        audioguide_link=content['audioguide_link'],
        description=content['description'],
        city_id=content['city_id'],
        name=content['name'],
        second_name=content['second_name'],
        patronymic=content['patronymic'],
        birthdate=content['birthdate'],
        deathdate=content['deathdate'],
        categories=categories,
        related_objects=related_objects,
    )

    session.add(historical_person)

    session.commit()
    session.close()

    return 'ok'


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['POST'])
@expects_json(put_historical_person_schema)
@returns_json
def post_hisrorical_person_by_id(object_id):
    if HistoricalPerson.query.get(object_id) is None:
        abort(404, 'Historical person not found')
        return

    content = g.data

    if City.query.get(content['city_id']) is None:
        abort(400, 'City with such id not found')
        return

    session = get_session()

    historical_person = session.query(HistoricalPerson).get(object_id)
    historical_person.image_link = content['image_link']
    historical_person.audioguide_link = content['audioguide_link']
    historical_person.description = content['description']
    historical_person.city_id = content['city_id']
    historical_person.name = content['name']
    historical_person.second_name = content['second_name']
    historical_person.patronymic = content['patronymic']
    historical_person.birthdate = content['birthdate']
    historical_person.deathdate = content['deathdate']

    categories = []

    for category_id in content['categories']:
        category = session.query(Category).get(category_id)

        if category is None:
            session.rollback()
            session.close()
            abort(400, 'Category not found')
            return

        categories.append(category)

    historical_person.categories = categories

    related_objects = []

    for object_id in content['related_objects']:
        object = session.query(Object).get(object_id)

        if object is None:
            session.rollback()
            session.close()
            abort(400, 'Object not found')
            return

        related_objects.append(object)

    historical_person.related_objects = related_objects

    session.commit()
    session.close()

    return 'ok'


@historical_person_blueptint.route('/historical_persons/<object_id>', methods=['DELETE'])
@returns_json
def delete_hisrorical_person_by_id(object_id):
    session = get_session()
    historical_person = session.query(HistoricalPerson).get(object_id)

    if historical_person is None:
        session.close()
        abort(404, 'Historical person not found')
        return

    session.delete(historical_person)
    session.commit()
    session.close()

    return 'ok'
