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
        nullable=False)
    description = db.Column(
        db.Text,
        name="route_description",
        nullable=False)
    objects = relationship(
        "RouteObjectInfo",
        order_by=RouteObjectInfo.__table__.c.route_object_order,
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
            'distance': self.get_total_distance()
        }

    def to_view_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'objectsCount': len(self.objects),
            'distance': self.get_total_distance()
        }

    def get_total_distance(self):
        session = get_session()

        geo_points = ""

        for obj in self.objects:

            entity = session.query(Entity).get(obj.object_id)

            geo_place = session.query(self.get_entity_type(entity)).get(entity.id)

            geolocation = geo_place.geolocation
            geo_points = geo_points + str(geolocation.longtude) + "," + str(geolocation.latitude) + ";"

        session.close()

        geo_points = geo_points[:-1]

        # car => foot
        url = 'http://router.project-osrm.org/route/v1/car/' + geo_points
        payload = {"steps": "true", "geometries": "geojson"}
        response = requests.get(url, params=payload)
        data = response.json()

        if 'routes' in data:
            return data['routes'][0]['distance']
        else:
            return ''

    @staticmethod
    def get_entity_type(entity):
        entity_type_name = entity.type.name
        switcher = {
            'place': Place,
            'public_place': PublicPlace,
        }
        return switcher.get(entity_type_name, "Invalid entity name in route")
