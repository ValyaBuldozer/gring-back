from models.base import db
from models.EntityType import EntityType
from models.Object import Object
from sqlalchemy.orm import relationship
from statistics import mean


class Place(Object):

    __tablename__ = "place"
    id = db.Column(
        db.Integer,
        db.ForeignKey("object.object_id"),
        primary_key=True,
        name="object_id",
        nullable=False
    )
    name = db.Column(
        db.String(100),
        name="place_name",
        nullable=False
    )
    address = db.Column(
        db.String(200),
        name="place_address",
        default="",
        nullable=False
    )
    geolocation_id = db.Column(
        db.Integer,
        db.ForeignKey("geolocation.geolocation_id"),
        name="place_geolocation_id",
        nullable=False,
    )
    geolocation = relationship(
        "Geolocation",
        cascade="all, delete-orphan",
        single_parent=True
    )
    routes = relationship(
        "RoutePlaceInfo",
        cascade="all, delete-orphan",
        single_parent=True
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.place
    }

    def get_name(self):
        return self.name

    def to_json(self):
        object_json = super().to_json()
        place_json = {
            'address': self.address,
            'geolocation': self.geolocation,
            'routes': list(
                map(lambda r: r.route_id, self.routes)),
        }

        return {
            **object_json,
            **place_json
        }
