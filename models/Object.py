from models.base import db
from models.ObjectType import ObjectType
from sqlalchemy.orm import relationship
from models.CategoryObject import CategoryObject
from abc import ABCMeta, abstractmethod


class Object(db.Model):

    __metaclass__ = ABCMeta
    __tablename__ = "object"
    id = db.Column(db.Integer, primary_key=True, name="object_id", nullable=False)
    type = db.Column(db.Enum(ObjectType), name="object_type", nullable=False)
    image_link = db.Column(db.String(250), name="object_image_link")
    audioguide_link = db.Column(db.String(250), name="object_audioguide_link")
    description = db.Column(db.Text, name="object_description")
    city_id = db.Column(
        db.Integer, db.ForeignKey("city.city_id"), name="object_city_id", nullable=False
    )
    city = relationship("City")
    categories = relationship("Category", secondary=CategoryObject)

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.object,
        'polymorphic_on': type
    }

    @abstractmethod
    def get_name():
        raise NotImplementedError("Must override method get_name")

    def to_json(self):
        return self.to_base_json()

    # we need it because some times we need not to call child's to_json() func
    def to_base_json(self):
        return {
            'id': self.id,
            'name': self.get_name(),
            'type': self.type.name,
            'image_link': self.image_link,
            'audioguide_link': self.audioguide_link,
            'categories': self.categories
        }
