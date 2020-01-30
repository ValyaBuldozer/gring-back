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

    def get_name(self):
        return self.name

    def to_json(self):
        object_json = super().to_json()
        place_json = {
            'address': self.address,
            'geolocation': self.geolocation,
            'timetable': self.timetable
        }

        return {
            **object_json,
            **place_json
        }
