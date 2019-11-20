from flask import Blueprint, request, abort, g
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
    reviews = Review.query.all()

    return to_json(reviews)


put_review_schema = {
    'type': 'object',
    'properties': {
        'user_id': {'type': 'integer'},
        'raiting': {'type': 'integer', 'minimum': 1, 'maximum': 5},
        'text': {'type': 'string'}
    },
    'required': ['user_id', 'raiting']
}


@review_blueptint.route('/reviews/<object_id>', methods=['PUT'])
@expects_json(put_review_schema)
@returns_json
def put_new_review(object_id):
    if Object.query.get(object_id) is None:
        abort(404, 'Object not found')
        return

    content = g.data
    session = get_session()
    review = Review(
        user_id=content['user_id'],
        object_id=object_id,
        raiting=content['raiting'],
        time=datetime.now(),
        text=content['text']
    )
    
    session.add(review)
    session.commit()
    session.close()

    return 'ok'
