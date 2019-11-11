from models.base import db
from models.ObjectType import ObjectType
from models.Object import Object


class Place(Object):

    __tablename__ = "public_place"
    id = db.Column(
        db.Integer, db.ForeignKey("object.object_id"), primary_key=True, name="object_id", nullable=True
    )
    name = db.Column(db.String(100), name="place_name", nullable=False)
    address = db.Column(db.String(200), name="place_address", default="", nullable=False)
    geolocation_id = db.Column(db.Integer(11), name="place_geolocation_id", nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.public_place
    }

