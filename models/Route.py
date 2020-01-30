from models.base import db
from sqlalchemy.orm import relationship
from models.RoutePlaceInfo import RoutePlaceInfo
from models.Entity import Entity
from models.Place import Place
from models.PublicPlace import PublicPlace
from models.EntityType import EntityType
from models.base import get_session
import util.osrm_client
import osrm


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
    objects = relationship(
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
            'objects': self.objects,
        }

    def to_view_json(self):
        distance, duration = self.get_osrm_foot_info()
        return {
            'id': self.id,
            'name': self.name,
            'objectsCount': len(self.objects),
            'distance': distance,
            'duration': duration
        }

    def get_osrm_foot_info(self):
        session = get_session()

        geo_points = []

        for obj in self.objects:

            geo_place = session.query(Place).get(obj.place_id)

            geolocation = geo_place.geolocation

            geo_point = [geolocation.longtude, geolocation.latitude]
            geo_points.append(geo_point)

        session.close()

        response = util.osrm_client.client.route(
            coordinates=geo_points,
            overview=osrm.overview.full)

        if 'routes' in response:
            return response['routes'][0]['distance'], response['routes'][0]['duration']
        else:
            return '', ''
