from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.LocaleString import LocaleString
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
    description_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="route_place_description_id",
        nullable=True
    )
    description = relationship(
        LocaleString,
        foreign_keys=[description_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    audioguide = db.Column(
        db.String(250),
        name="route_place_audioguide_link",
        nullable=True
    )

    def to_json(self, locale):
        object_dict = self.place.to_base_json(locale)
        description = self.description.get(locale)

        return {
            **object_dict,
            "description": object_dict["description"] if description is None else description,
            "audioguide": object_dict["audioguide"] if self.audioguide is None else self.audioguide
        }
