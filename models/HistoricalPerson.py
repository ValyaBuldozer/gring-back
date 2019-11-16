from models.base import db
from models.ObjectType import ObjectType
from models.Object import Object


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

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.historical_person
    }

    def get_name(self):
        # TODO: only for Russian language
        if len(self.patronymic) > 0:
            return ("%s. %s. %s" % (self.name[0], self.patronymic[0], self.second_name))
        else:
            return self.name + " " + self.second_name
