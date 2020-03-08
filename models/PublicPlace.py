from models.Language import Language
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
            'geolocation': self.geolocation,
            'timetable': self.timetable
        }

        return {
            **object_json,
            **place_json
        }
