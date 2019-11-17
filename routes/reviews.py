from flask import Blueprint, request, abort, g
from util.json import returns_json, to_json
from models.Review import Review
from flask_expects_json import expects_json


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


@review_blueptint.route('/reviews', methods=['PUT'])
@expects_json(put_review_schema)
@returns_json
def put_new_review():
    content = g.data

    return 'woah'
