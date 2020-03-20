from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from models.base import db
from models.LocaleString import LocaleString


class Category(db.Model):

    __tablename__ = "category"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="category_id",
        nullable=False
    )
    alias = db.Column(
        db.String(30),
        name="category_alias",
        nullable=False
    )
    name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="category_name_id",
        nullable=False
    )
    name = relationship(
        LocaleString,
        foreign_keys=[name_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )

    def to_json(self, locale):
        return {
            'id': self.id,
            'name': self.name.get(locale)
        }
