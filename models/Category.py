from models.base import db
from models.CategoryObject import CategoryObject
from sqlalchemy.orm import relationship


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="category_id",
        nullable=False
    )
    name = db.Column(
        db.String(30),
        name="category_name",
        nullable=False
    )
    # objects = relationship(
    #     "Object",
    #     secondary=CategoryObject,
    #     backref=db.backref('category')
    # )

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }
