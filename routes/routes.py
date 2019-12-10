from flask import Blueprint, request, abort, g
from util.json import to_json, returns_json
from models.Route import Route
from models.RouteObjectInfo import RouteObjectInfo
from models.Object import Object
from models.base import get_session
from flask_expects_json import expects_json


routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/routes', methods=['GET'])
@returns_json
def get_routes():
    object_id = request.args.get('object')

    routes = Route.query.filter(
        Route.objects.any(RouteObjectInfo.object_id == object_id) if object_id is not None else True
    ).all()

    return to_json(routes, lambda r: r.to_view_json())


@routes_blueprint.route('/routes/<route_id>', methods=['GET'])
@returns_json
def get_route_by_id(route_id):

    route = Route.query.get(route_id)

    if route is None:
        abort(404, 'Route not found')

    return to_json(route)


put_route_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'objects': {
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
    'required': ['name', 'description', 'objects']
}


@routes_blueprint.route('/routes/', methods=['PUT'])
@expects_json(put_route_schema)
@returns_json
def put_new_route():

    content = g.data
    session = get_session()

    objects = []

    for index, object_info in enumerate(content['objects']):
        if session.query(Object).get(object_info['id']) is None:
            session.rollback()
            session.close()
            abort(400, "Object with id = %s not found" % (object_info['id']))
            return

        objects.append(RouteObjectInfo(
            object_id=object_info['id'],
            description=object_info.get('description', None),
            order=index,
            audioguide=object_info.get('audioguide', None)
        ))

    session.add(Route(
        name=content['name'],
        description=content['description'],
        objects=objects
    ))

    session.commit()
    session.close()

    return 'ok'
