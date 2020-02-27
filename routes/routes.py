from flask import Blueprint, request, abort, g
from util.json import to_json, returns_json
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

    json_routes = to_json(routes, lambda r: r.to_view_json())

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

    json_route = to_json(route)

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
@returns_json
@roles_required([RoleName.admin, RoleName.content_moder])
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

    session.add(Route(
        name=content['name'],
        description=content['description'],
        places=places
    ))

    session.commit()
    session.close()

    return 'ok'


@routes_blueprint.route('/routes/<route_id>', methods=['POST'])
@expects_json(put_route_schema)
@returns_json
@roles_required([RoleName.admin, RoleName.content_moder])
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

    route.name = content['name']
    route.description = content['description']
    route.places = places

    session.commit()
    session.close()

    return 'ok'


@routes_blueprint.route('/routes/<route_id>', methods=['DELETE'])
@returns_json
@roles_required([RoleName.admin, RoleName.content_moder])
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
