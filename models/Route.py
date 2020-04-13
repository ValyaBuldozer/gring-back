from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.LocaleString import LocaleString
from models.base import db
from sqlalchemy.orm import relationship
from models.RoutePlaceInfo import RoutePlaceInfo
from models.Entity import Entity
from models.EntityType import EntityType
from util import osrm_client
import osrm
from statistics import mean


class Route(Entity):

    __tablename__ = "route"
    id = db.Column(
        db.Integer,
        db.ForeignKey("entity.entity_id"),
        primary_key=True,
        name="route_id",
        nullable=False
    )
    name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="route_name_id",
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
    description_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="route_description_id",
        nullable=False
    )
    description = relationship(
        LocaleString,
        foreign_keys=[description_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    places = relationship(
        "RoutePlaceInfo",
        order_by=RoutePlaceInfo.__table__.c.route_place_order,
        cascade="all, delete-orphan",
        single_parent=True
    )
    __mapper_args__ = {
        'polymorphic_identity': EntityType.route
    }

    def get_name(self, locale):
        return self.name.get(locale)

    def get_image(self):
        return None if len(self.places) < 1 else self.places[0].place.image_link

    def to_json(self, locale):
        return {
            **self.to_view_json(locale),
            'description': self.description.get(locale),
            'places': self.places,
        }

    def to_view_json(self, locale):
        distance, duration = self.get_osrm_foot_info()
        places_count = len(self.places)

        return {
            'id': self.id,
            'name': self.name.get(locale),
            'city': self.city.to_attribute_json(locale),
            'placesCount': places_count,
            'distance': distance,
            'duration': duration,
            'image': self.get_image(),
            'rating': {
                'average': self.avg_rating(),
                'count': len(self.reviews)
            }
        }

    def get_osrm_foot_info(self):
        geo_points = []

        for place_info in self.places:
            geolocation = place_info.place.geolocation

            geo_point = [geolocation.longitude, geolocation.latitude]
            geo_points.append(geo_point)

        response = osrm_client.client.route(
            coordinates=geo_points,
            overview=osrm.overview.full)

        if 'routes' in response:
            return response['routes'][0]['distance'], response['routes'][0]['duration']
        else:
            return '', ''
