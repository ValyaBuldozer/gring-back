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
    patronymic = db.Column(db.String(30), name="person_patronymic", nullable=False)
    birthdate = db.Column(db.Date, name="person_birthdate", nullable=False)
    deathdate = db.Column(db.Date, name="person_deathdate")

    __mapper_args__ = {
        'polymorphic_identity': ObjectType.historical_person
    }