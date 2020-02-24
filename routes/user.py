from flask import Blueprint, g, request, abort, jsonify
from util.json import to_json
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from models.base import get_session
from models.User import User
from models.Place import Place
from flask_expects_json import expects_json


user_page_blueprint = Blueprint('user', __name__)


@user_page_blueprint.route('/user/favorite', methods=['GET'])
@jwt_required
def get_user_favorite_place_by_id():
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    json_place = to_json(user.favorite_places)

    session.close()

    return json_place


put_favorite_schema = {
    'type': 'object',
    'properties': {
        'place_id': {'type': 'integer'},
    },
    'required': ['place_id']
}


@user_page_blueprint.route('/user/favorite/', methods=['POST'])
@expects_json(put_favorite_schema)
@jwt_required
def add_new_favorite_place():
    content = g.data
    session = get_session()

    place_id = content['place_id']
    favorite_place = session.query(Place).get(place_id)

    if favorite_place is None:
        session.close()
        abort(400, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()

    user = session.query(User).filter(
        User.id == current_user_id
    ).first()

    if any(place.id == favorite_place.id for place in user.favorite_places):
        abort(400, "Place with id = %s already added to favorites" % favorite_place.id)
        return

    user.favorite_places.append(favorite_place)

    session.commit()
    session.close()

    return 'ok'


@user_page_blueprint.route('/user/favorite/<place_id>', methods=['DELETE'])
@jwt_required
def delete_favorite_place(place_id):
    session = get_session()
    favorite_place = session.query(Place).get(place_id)

    if favorite_place is None:
        session.close()
        abort(404, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()

    user = session.query(User).filter(
        User.id == current_user_id
    ).first()

    user.favorite_places.remove(favorite_place)

    session.commit()
    session.close()

    return 'ok'
