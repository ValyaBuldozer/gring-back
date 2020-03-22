from flask import Blueprint, request, abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.Entity import Entity
from models.User import User
from util.json import returns_json, convert_to_json
from models.Review import Review
from models.Object import Object
from models.base import get_session
from flask_expects_json import expects_json
from datetime import datetime
from util.decorators import roles_required
from models.RoleName import RoleName
from util.current_user import get_current_user


review_blueptint = Blueprint('reviews', __name__)


@review_blueptint.route('/reviews', methods=['GET'])
@returns_json
def get_reviews():
    entity_id = request.args.get('object')
    limit = request.args.get('limit')

    session = get_session()

    reviews = session.query(Review).filter(
        Review.entity_id == entity_id if entity_id is not None else True
    ).limit(limit).all()

    json_reviews = convert_to_json(reviews)

    session.close()

    return json_reviews


put_review_schema = {
    'type': 'object',
    'properties': {
        'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
        'text': {'type': 'string'}
    },
    'required': ['rating']
}


@review_blueptint.route('/reviews/<entity_id>', methods=['PUT'])
@expects_json(put_review_schema)
@roles_required([RoleName.user])
def put_new_review(entity_id):
    session = get_session()

    if session.query(Entity).get(entity_id) is None:
        session.close()
        abort(404, 'Entity not found')
        return

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    review = session.query(Review).filter(
        Review.user_id == user.id,
        Review.entity_id == entity_id
    ).first()

    if review is not None:
        session.close()
        abort(400, "User with id = %s already has a review for entity with id = %s" % (user.id, entity_id))
        return

    user_id = get_jwt_identity()
    content = g.data
    review = Review(
        user_id=user_id,
        entity_id=entity_id,
        rating=content['rating'],
        time=datetime.now(),
        text=content['text']
    )
    
    session.add(review)
    session.commit()
    session.close()

    return 'ok'


@review_blueptint.route('/reviews/<entity_id>', methods=['DELETE'])
@roles_required([RoleName.user])
def delete_own_review_by_id(entity_id):
    session = get_session()

    current_user_id = get_jwt_identity()
    user = session.query(User).get(current_user_id)

    review = session.query(Review).filter(
        Review.user_id == user.id,
        Review.entity_id == entity_id
    ).first()

    if review is None:
        session.close()
        abort(404, "User with id = %s didn't add review to entity with id = %s yet" % (user.id, entity_id))
        return

    session.delete(review)
    session.commit()
    session.close()

    return 'ok'

