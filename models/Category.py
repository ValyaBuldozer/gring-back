from models.base import db
from models.ObjectType import ObjectType


class Category(db.Model):

    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, name="category_id")
    name = db.Column(db.String(20), name="category_name")
    object_type = db.Column(db.Enum(ObjectType), name="object_type")
