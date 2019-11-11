from models.base import db
from models.ObjectType import ObjectType
from models.Object import Object
from sqlalchemy.orm import relationship
from models.Geolocation import Geolocation


class PublicPlace(Object):

    __tablename__ = "public_place"
    id = db.Column(
        db.Integer, db.ForeignKey("object.object_id"), primary_key=True, name="object_id", nullable=False
    )
    name = db.Column(db.String(100), name="place_name", nullable=False)
    address = db.Column(db.String(200), name="place_address", default="", nullable=False)
    geolocation_id = db.Column(
        db.Integer, db.ForeignKey("geolocation.geolocation_id"), name="place_geolocation_id", nullable=False
    )
    geolocation = relationship("Geolocation")

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.public_place
    }

