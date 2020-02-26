from models.base import db
from sqlalchemy.orm import relationship
from models.RoutePlaceInfo import RoutePlaceInfo
from models.Entity import Entity
from models.EntityType import EntityType
import util.osrm_client
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
    name = db.Column(
        db.String(100),
        name="route_name",
        nullable=False
    )
    description = db.Column(
        db.Text,
        name="route_description",
        nullable=False
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

    def to_json(self):
        return {
            **self.to_view_json(),
            'description': self.description,
            'places': self.places,
        }

    def to_view_json(self):
        distance, duration = self.get_osrm_foot_info()
        places_count = len(self.places)
        image = None if places_count < 1 else self.places[0].place.image_link

        return {
            'id': self.id,
            'name': self.name,
            'placesCount': places_count,
            'distance': distance,
            'duration': duration,
            'image': image,
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

        response = util.osrm_client.client.route(
            coordinates=geo_points,
            overview=osrm.overview.full)

        if 'routes' in response:
            return response['routes'][0]['distance'], response['routes'][0]['duration']
        else:
            return '', ''
