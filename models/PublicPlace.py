from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.LocaleString import LocaleString
from models.base import db
from models.EntityType import EntityType
from models.Place import Place
from sqlalchemy.orm import relationship


class PublicPlace(Place):

    __tablename__ = "public_place"
    id = db.Column(
        db.Integer,
        db.ForeignKey("place.object_id"),
        primary_key=True,
        name="object_id",
        nullable=False
    )
    phone_number = db.Column(
        db.String(15),
        name="public_place_phone_number",
        nullable=True
    )
    site = db.Column(
        db.String(100),
        name="public_place_site",
        nullable=True
    )
    avg_bill_id = db.Column(
        db.String(50),
        db.ForeignKey("locale_string.string_id"),
        name="public_place_avg_bill_id",
        nullable=True
    )
    avg_bill = relationship(
        LocaleString,
        foreign_keys=[avg_bill_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    visit_cost_id = db.Column(
        db.String(50),
        db.ForeignKey("locale_string.string_id"),
        name="public_place_visit_cost_id",
        nullable=True
    )
    visit_cost = relationship(
        LocaleString,
        foreign_keys=[visit_cost_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    timetable = relationship(
        "Timetable",
        cascade="all, delete-orphan",
        single_parent=True
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.public_place
    }

    def get_name(self, locale):
        return self.name.get(locale)

    def to_json(self, locale):
        object_json = super().to_json(locale)
        place_json = {
            'address': self.address.get(locale),
            'phone_number': self.phone_number,
            'site': self.site,
            'avg_bill': self.avg_bill.get(locale),
            'geolocation': self.geolocation,
            'timetable': self.timetable
        }

        return {
            **object_json,
            **place_json
        }
