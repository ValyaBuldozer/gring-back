from flask import Blueprint, g, request, abort, jsonify
from flask_jwt_extended import (
    get_jwt_identity, jwt_required
)
from models.base import get_session
from models.User import User
from models.Place import Place
from models.UserFavoritePlace import UserFavoritePlace
from flask_expects_json import expects_json


user_page_blueprint = Blueprint('user_page', __name__)


put_favorite_schema = {
    'type': 'object',
    'properties': {
        'place_id': {'type': 'integer'},
    },
    'required': ['place_id']
}


@user_page_blueprint.route('/user_page/favorite_place/', methods=['POST'])
@expects_json(put_favorite_schema)
@jwt_required
def add_new_favorite_place():
    content = g.data
    session = get_session()

    place_id = content['place_id']
    place = session.query(Place).get(place_id)

    if place is None:
        session.close()
        abort(400, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()

    user = session.query(User).filter(
        User.id == current_user_id
    ).first()

    place = session.query(Place).get(place_id)

    user.favorite_places.append(place)

    session.commit()
    session.close()

    return 'ok'


@user_page_blueprint.route('/user_page/favorite_place/<place_id>', methods=['DELETE'])
@jwt_required
def delete_favorite_place(place_id):
    session = get_session()
    place = session.query(Place).get(place_id)

    if place is None:
        session.close()
        abort(404, "Place with id = %s not found" % place_id)
        return

    current_user_id = get_jwt_identity()

    user = session.query(User).filter(
        User.id == current_user_id
    ).first()

    user.favorite_places.remove(place)

    session.commit()
    session.close()

    return 'ok'
