from models.base import db
from sqlalchemy.orm import relationship
from models.RouteObjectInfo import RouteObjectInfo
from models.Entity import Entity
from models.EntityType import EntityType


class Route(Entity):

    __tablename__ = "route"
    id = db.Column(
        db.Integer,
        db.ForeignKey("entity.entity_id"),
        primary_key=True,
        name="route_id",
        nullable=False
    )
    name = db.Column(db.String(100), name="route_name", nullable=False)
    description = db.Column(db.Text, name="route_description", nullable=False)
    objects = relationship(
        "RouteObjectInfo",
        order_by=RouteObjectInfo.__table__.c.route_object_order,
        cascade="all, delete-orphan", single_parent=True
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.route
    }

    def to_json(self):
        return {
            **self.to_view_json(),
            'description': self.description,
            'objects': self.objects
        }

    def to_view_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'objectsCount': len(self.objects)
        }
