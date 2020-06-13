from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.LocaleLink import LocaleLink
from models.LocaleString import LocaleString
from models.base import db
from models.EntityType import EntityType
from sqlalchemy.orm import relationship
from models.Entity import Entity
from models.CategoryObject import CategoryObject
from abc import ABCMeta, abstractmethod


class Object(Entity):

    __metaclass__ = ABCMeta
    __tablename__ = "object"
    id = db.Column(
        db.Integer,
        db.ForeignKey("entity.entity_id"),
        primary_key=True,
        name="object_id",
        nullable=False
    )
    image_link = db.Column(
        db.String(250),
        name="object_image_link",
        nullable=False
    )
    audioguide_link_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_link.link_id", ondelete="SET NULL"),
        name="object_audioguide_link_id",
        nullable=True
    )
    audioguide_link = relationship(
        LocaleLink,
        foreign_keys=[audioguide_link_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    description_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="object_description_id",
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
    categories = relationship(
        "Category",
        secondary=CategoryObject,
        single_parent=True,
        backref=db.backref('object')
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.object
    }

    @abstractmethod
    def get_name(self, locale):
        raise NotImplementedError("Must override method get_name")

    def get_image(self):
        return self.image_link

    def to_json(self, locale):
        return self.to_object_json(locale)

    # we need it because some times we need not to call child's to_json() func
    def to_object_json(self, locale):
        return {
            'id': self.id,
            'name': self.get_name(locale),
            'city': self.city.to_attribute_json(locale),
            'type': self.type.name,
            'image': self.image_link,
            'audioguide': self.audioguide_link.get(locale),
            'categories': self.categories,
            'rating': {
                'average': self.avg_rating(),
                'count': len(self.reviews)
            }
        }
