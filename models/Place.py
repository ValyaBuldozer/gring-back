from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.LocaleString import LocaleString
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
    name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="place_name_id",
        nullable=False
    )
    name = relationship(
        LocaleString,
        foreign_keys=[name_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    address_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="place_address_id",
        nullable=False
    )
    address = relationship(
        LocaleString,
        foreign_keys=[address_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
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

    def get_name(self, locale):
        return self.name.get(locale)

    def to_json(self, locale):
        object_json = super().to_json(locale)
        place_json = {
            'address': self.address.get(locale),
            'geolocation': self.geolocation,
            'description': self.description.get(locale),
            'routes': list(
                map(lambda r: r.route_id, self.routes)),
        }

        return {
            **object_json,
            **place_json
        }
