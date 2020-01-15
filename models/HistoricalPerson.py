from models.base import db
from sqlalchemy.orm import relationship
from models.EntityType import EntityType
from models.Object import Object
from models.HistoricalPersonRelatedObjects import HistoricalPersonRelatedObjects


class HistoricalPerson(Object):

    __tablename__ = "historical_person"
    id = db.Column(
        db.Integer, db.ForeignKey("object.object_id"), primary_key=True, name="object_id", nullable=False
    )
    name = db.Column(db.String(20), name="person_name", nullable=False)
    second_name = db.Column(db.String(30), name="person_second_name", nullable=False)
    patronymic = db.Column(db.String(30), name="person_patronymic", nullable=False, default="")
    birthdate = db.Column(db.Date, name="person_birthdate", nullable=False)
    deathdate = db.Column(db.Date, name="person_deathdate")
    related_objects = relationship("Object", secondary=HistoricalPersonRelatedObjects, single_parent=True,
                                   backref=db.backref('historical_person'))

    __mapper_args__ = {
        'polymorphic_identity': EntityType.historical_person
    }

    def get_name(self):
        # TODO: only for Russian language
        if len(self.patronymic) > 0:
            return ("%s. %s. %s" % (self.name[0], self.patronymic[0], self.second_name))
        else:
            return self.name + " " + self.second_name

    def to_json(self):
        object_json = super().to_json()
        person_json = {
            'name': self.name,
            'secondName': self.second_name,
            'patronymic': self.patronymic if self.patronymic is not '' else None,
            'birthdate': str(self.birthdate),
            'deathdate': str(self.deathdate) if self.deathdate is not None else None,
            'relatedObjects': list(map(lambda o: o.to_base_json(), self.related_objects))
        }

        return {
            **object_json,
            **person_json
        }
