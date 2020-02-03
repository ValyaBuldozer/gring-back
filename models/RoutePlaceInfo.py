from models.base import db
from sqlalchemy.orm import relationship


class RoutePlaceInfo(db.Model):
    place_id = db.Column(
        db.Integer,
        db.ForeignKey("place.object_id"),
        primary_key=True,
        name="place_id",
        nullable=False
    )
    place = relationship(
        "Place"
    )
    route_id = db.Column(
        db.Integer,
        db.ForeignKey("route.route_id"),
        primary_key=True,
        name="route_id",
        nullable=False
    )
    route = relationship(
        "Route"
    )
    order = db.Column(
        db.Integer,
        name="route_place_order",
        nullable=False
    )
    description = db.Column(
        db.Text,
        name="route_place_description",
        nullable=True
    )
    audioguide = db.Column(
        db.String(250),
        name="route_place_audioguide_link",
        nullable=True
    )

    def to_json(self):
        object_dict = self.object.to_base_json()

        return {
            **object_dict,
            "description": object_dict["description"] if self.description is None else self.description,
            "audioguide": object_dict["audioguide"] if self.audioguide is None else self.audioguide
        }
