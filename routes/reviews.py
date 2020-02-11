from flask import Blueprint, request, abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from util.json import returns_json, to_json
from models.Review import Review
from models.Object import Object
from models.base import get_session
from flask_expects_json import expects_json
from datetime import datetime


review_blueptint = Blueprint('reviews', __name__)


@review_blueptint.route('/reviews', methods=['GET'])
@returns_json
def get_reviews():
    object_id = request.args.get('object')
    limit = request.args.get('limit')

    session = get_session()

    reviews = session.query(Review).filter(
        Review.entity_id == object_id if object_id is not None else True
    ).limit(limit).all()

    json_reviews = to_json(reviews)

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


@review_blueptint.route('/reviews/<object_id>', methods=['PUT'])
@expects_json(put_review_schema)
@jwt_required
@returns_json
def put_new_review(object_id):
    session = get_session()

    if session.query(Object).get(object_id) is None:
        abort(404, 'Object not found')
        return

    user_id = get_jwt_identity()
    content = g.data
    review = Review(
        user_id=user_id,
        object_id=object_id,
        rating=content['rating'],
        time=datetime.now(),
        text=content['text']
    )
    
    session.add(review)
    session.commit()
    session.close()

    return 'ok'
