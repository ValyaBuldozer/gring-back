from models.base import db
from models.EntityType import EntityType
from sqlalchemy.orm import relationship
from models.CategoryObject import CategoryObject
from abc import ABCMeta, abstractmethod
from statistics import mean


class Entity(db.Model):

    __tablename__ = 'entity'
    id = db.Column(db.Integer, primary_key=True, name="entity_id", nullable=False)
    type = db.Column(db.Enum(EntityType), name="entity_type", nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': EntityType.entity,
        'polymorphic_on': type
    }
