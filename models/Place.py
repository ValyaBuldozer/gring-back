from models.base import db
from models.ObjectType import ObjectType
from models.Object import Object


class Place(Object):

    __tablename__ = "place"
    id = db.Column(
        db.Integer, db.ForeignKey('object.object_id'), primary_key=True, name="object_id"
    )
    name = db.Column(db.String(100), name="place_name")
    address = db.Column(db.String(200), name="place_address", default="")

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.place
    }
