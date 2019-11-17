from models.base import db
from sqlalchemy.orm import relationship
from models.RouteObjectInfo import RouteObjectInfo


class Route(db.Model):

    __tablename__ = "route"
    id = db.Column(db.Integer, primary_key=True, name="route_id", nullable=False)
    name = db.Column(db.String(100), name="route_name", nullable=False)
    description = db.Column(db.Text, name="route_description", nullable=False)
    objects = relationship(
        "Object", secondary=RouteObjectInfo, order_by=RouteObjectInfo.c.route_object_order
    )

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'objects': list(map(lambda o: o.to_base_json(), self.objects))
        }
