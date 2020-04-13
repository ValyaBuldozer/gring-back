from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from models.LocaleString import LocaleString
from models.base import db


class City(db.Model):

    __tablename__ = "city"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="city_id",
        nullable=False
    )
    name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="city_name_id",
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
    image_link = db.Column(
        db.String(250),
        name="city_image_link",
        nullable=False
    )
    description_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="city_description_id",
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

    def to_attribute_json(self, locale):
        return {
            'id': self.id,
            'name': self.name.get(locale),
        }

    def to_json(self, locale):
        return {
            'id': self.id,
            'name': self.name.get(locale),
            'description': self.description.get(locale),
            'image_link': self.image_link,
        }

