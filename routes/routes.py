from flask import Blueprint, request, abort
from util.json import to_json, returns_json
from models.Route import Route


routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/routes', methods=['GET'])
@returns_json
def get_routes():
    routes = Route.query.all()

    return to_json(routes)
