from models.base import db
from sqlalchemy.orm import relationship


class Place(db.Model):

    __tablename__ = "place"
    id = db.Column(
        db.Integer, db.ForeignKey("object.object_id"), primary_key=True, name="object_id"
    )
    object = relationship("Object")
    name = db.Column(db.String(100), name="place_name", nullable=False)
    address = db.Column(db.String(200), name="place_address", nullable=False)
    geolocation_id = db.Column(db.Integer(11), name="place_geolocation_id", nullable=True)

    __tablename__ = "place"
    id = db.Column(
        db.Integer, db.ForeignKey('object.object_id'), primary_key=True, name="object_id"
    )
    name = db.Column(db.String(100), name="place_name")
    address = db.Column(db.String(200), name="place_address", default="")

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.place
    }