from sqlalchemy.orm.collections import attribute_mapped_collection

from models.Language import Language
from models.base import db
from sqlalchemy.orm import relationship
from models.EntityType import EntityType
from models.Object import Object
from models.HistoricalPersonRelatedObjects import HistoricalPersonRelatedObjects
from models.LocaleString import LocaleString


class HistoricalPerson(Object):

    __tablename__ = "historical_person"
    id = db.Column(
        db.Integer,
        db.ForeignKey("object.object_id"),
        primary_key=True,
        name="object_id",
        nullable=False
    )
    name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="person_name_id",
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
    second_name_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="person_second_name_id",
        nullable=False
    )
    second_name = relationship(
        LocaleString,
        foreign_keys=[second_name_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    patronymic_id = db.Column(
        db.String(36),
        db.ForeignKey("locale_string.string_id"),
        name="person_patronymic_id",
        nullable=True
    )
    patronymic = relationship(
        LocaleString,
        foreign_keys=[patronymic_id],
        uselist=True,
        single_parent=True,
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection('locale')
    )
    birthdate = db.Column(
        db.Date,
        name="person_birthdate",
        nullable=False
    )
    deathdate = db.Column(
        db.Date,
        name="person_deathdate"
    )
    related_objects = relationship(
        "Object",
        secondary=HistoricalPersonRelatedObjects,
        single_parent=True,
        backref=db.backref('historical_person')
    )

    __mapper_args__ = {
        'polymorphic_identity': EntityType.historical_person
    }

    def get_name(self, locale):
        name = self.name.get(locale)
        second_name = self.second_name.get(locale)
        patronymic = self.patronymic.get(locale)
        if name is not None and second_name is not None:
            if patronymic is not None:
                return ("%s. %s. %s" % (name[0],
                                        patronymic[0],
                                        second_name))
            else:
                return name + " " + second_name

    def to_json(self, locale):
        name = self.name.get(locale)
        second_name = self.second_name.get(locale)
        patronymic = self.patronymic.get(locale)
        object_json = super().to_json(locale)
        person_json = {
            'name': name,
            'secondName': second_name,
            'patronymic': patronymic,
            'birthdate': str(self.birthdate),
            'deathdate': str(self.deathdate) if self.deathdate is not None else None,
            'relatedObjects': list(map(lambda o: o.to_base_json(locale), self.related_objects))
        }

        return {
            **object_json,
            **person_json
        }
