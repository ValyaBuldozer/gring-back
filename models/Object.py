from models.base import db
from models.ObjectType import ObjectType
from sqlalchemy.orm import relationship
from models.City import City
from models.CategoryObject import CategoryObject
from models.Category import Category


class Object(db.Model):

    __tablename__ = "object"
    id = db.Column(db.Integer, primary_key=True, name="object_id")
    type = db.Column(db.Enum(ObjectType), name="object_type")
    image_link = db.Column(db.String(250), name="object_image_link")
    description = db.Column(db.Text, name="object_description")
    city_id = db.Column(
        db.Integer, db.ForeignKey("city.city_id"), name="object_city_id"
    )
    city = relationship("City")
    categories = relationship("Category", secondary=CategoryObject)

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.object,
        'polymorphic_on': type
    }
