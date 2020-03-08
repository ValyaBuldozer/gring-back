from uuid import uuid4

from flask import Blueprint, request, abort, g

from models.Language import Language
from models.LocaleString import LocaleString
from util.json import convert_to_json, returns_json, validate_locate
from models.Route import Route
from models.RoutePlaceInfo import RoutePlaceInfo
from models.Object import Object
from models.Place import Place
from models.base import get_session
from flask_expects_json import expects_json
from util.decorators import roles_required
from models.RoleName import RoleName


routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/routes', methods=['GET'])
@returns_json
def get_routes():
    session = get_session()

    object_id = request.args.get('object')

    routes = session.query(Route).filter(
        Route.places.any(RoutePlaceInfo.place_id == object_id) if object_id is not None else True
    ).all()

    locale = validate_locate(request.headers.get('locale'))
    mapped_objects = list(map(lambda r: r.to_view_json(locale), routes))

    json_routes = convert_to_json(mapped_objects, locale)

    session.close()

    return json_routes


@routes_blueprint.route('/routes/<route_id>', methods=['GET'])
@returns_json
def get_route_by_id(route_id):
    session = get_session()

    route = session.query(Route).get(route_id)

    if route is None:
        session.close()
        abort(404, "Route with id = %s not found" % route_id)

    locale = validate_locate(request.headers.get('locale'))
    json_route = convert_to_json(route, locale)

    session.close()

    return json_route


put_route_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'places': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'description': {'type': ['string', 'null']},
                    'audioguide': {'type': ['string', 'null']}
                },
                'required': ['id']
            }
        }
    },
    'required': ['name', 'description', 'places']
}


@routes_blueprint.route('/routes', methods=['PUT'])
@expects_json(put_route_schema)
@roles_required([RoleName.content_moder])
def put_new_route():
    content = g.data
    session = get_session()

    places = []

    for index, place_info in enumerate(content['places']):
        if session.query(Place).get(place_info['id']) is None:
            session.close()
            abort(400, "Place with id = %s not found" % (place_info['id']))
            return

        places.append(RoutePlaceInfo(
            place_id=place_info['id'],
            description=place_info.get('description', None),
            order=index,
            audioguide=place_info.get('audioguide', None)
        ))

    route = Route(
        places=places
    )

    locale = validate_locate(request.headers.get('locale'))

    name_id = str(uuid4())
    locale_string = LocaleString(
        id=name_id,
        locale=locale,
        text=content['name']
    )
    route.name_id = name_id
    route.name.set(locale_string)

    description_id = str(uuid4())
    locale_string = LocaleString(
        id=description_id,
        locale=locale,
        text=content['description']
    )
    route.description_id = description_id
    route.description.set(locale_string)

    session.add(route)

    session.commit()
    session.close()

    return 'ok'


@routes_blueprint.route('/routes/<route_id>', methods=['POST'])
@expects_json(put_route_schema)
@roles_required([RoleName.content_moder])
def post_route_by_id(route_id):
    session = get_session()
    route = session.query(Route).get(route_id)

    if route is None:
        session.close()
        abort(404, "Route with id = %s not found" % route_id)
        return

    content = g.data

    places = []

    for index, place_info in enumerate(content['places']):
        if session.query(Place).get(place_info['id']) is None:
            session.close()
            abort(400, "Place with id = %s not found" % (place_info['id']))
            return

        places.append(RoutePlaceInfo(
            place_id=place_info['id'],
            description=place_info.get('description', None),
            order=index,
            audioguide=place_info.get('audioguide', None)
        ))

    route.places = places

    locale = validate_locate(request.headers.get('locale'))

    if locale not in route.name:
        route.name.set(LocaleString(
            id=route.name_id,
            locale=locale,
            text=content['name']
        ))
    else:
        route.name.get(locale).text = content['name']

    if locale not in route.description:
        route.description.set(LocaleString(
            id=route.description_id,
            locale=locale,
            text=content['description']
        ))
    else:
        route.description.get(locale).text = content['description']

    session.commit()
    session.close()

    return 'ok'


@routes_blueprint.route('/routes/<route_id>', methods=['DELETE'])
@roles_required([RoleName.content_moder])
def delete_route_by_id(route_id):
    session = get_session()
    route = session.query(Route).get(route_id)

    if route is None:
        session.close()
        abort(404, "Route with id = %s not found" % route_id)
        return

    session.delete(route)
    session.commit()
    session.close()

    return 'ok'
