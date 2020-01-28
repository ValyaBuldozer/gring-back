from models.base import db
from sqlalchemy.orm import relationship
from models.RouteObjectInfo import RouteObjectInfo
from models.Entity import Entity
from models.Place import Place
from models.PublicPlace import PublicPlace
from models.EntityType import EntityType
from models.base import get_session
import osrm
import requests
from flask import current_app
from models.RoutingMachineInfo import RoutingMachineInfo


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
        "RouteObjectInfo",
        order_by=RouteObjectInfo.__table__.c.route_object_order,
        cascade="all, delete-orphan",
        single_parent=True
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.route
    }

    osrm_route_info = RoutingMachineInfo('', '')

    def to_json(self):
        self.osrm_route_info = self.get_osrm_foot_info()
        return {
            **self.to_view_json(),
            'description': self.description,
            'objects': self.objects,
            'distance': self.osrm_route_info.distance,
            'duration': self.osrm_route_info.duration
        }

    def to_view_json(self):
        self.osrm_route_info = self.get_osrm_foot_info()
        return {
            'id': self.id,
            'name': self.name,
            'objectsCount': len(self.objects),
            'distance': self.osrm_route_info.distance,
            'duration': self.osrm_route_info.duration
        }

    def get_osrm_foot_info(self):
        session = get_session()

        geo_points = ""

        for obj in self.objects:

            entity = session.query(Entity).get(obj.object_id)

            geo_place = session.query(self.get_entity_type(entity)).get(entity.id)

            geolocation = geo_place.geolocation
            geo_points = geo_points + str(geolocation.longtude) + "," + str(geolocation.latitude) + ";"

        session.close()

        geo_points = geo_points[:-1]

        url = current_app.config['OSRM_URL'] + 'foot/' + geo_points
        payload = {"steps": "true", "geometries": "geojson"}
        response = requests.get(url, params=payload)
        data = response.json()

        if 'routes' in data:
            return RoutingMachineInfo(data['routes'][0]['distance'], data['routes'][0]['duration'])

    @staticmethod
    def get_entity_type(entity):
        entity_type_name = entity.type.name
        switcher = {
            'place': Place,
            'public_place': PublicPlace,
        }
        return switcher.get(entity_type_name, "Invalid entity name in route")
