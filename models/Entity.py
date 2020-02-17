from models.base import db
from models.EntityType import EntityType
from sqlalchemy.orm import relationship
from models.CategoryObject import CategoryObject
from abc import ABCMeta, abstractmethod
from statistics import mean


class Entity(db.Model):
    __tablename__ = 'entity'
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="entity_id",
        nullable=False
    )
    type = db.Column(
        db.Enum(EntityType),
        name="entity_type",
        nullable=False
    )
    reviews = relationship(
        "Review",
        cascade="all, delete-orphan",
        single_parent=True
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.entity,
        'polymorphic_on': type
    }

    def avg_rating(self):
        if len(self.reviews) < 1:
            return 0

        return round(mean(map(lambda r: r.rating, self.reviews)), 2)
