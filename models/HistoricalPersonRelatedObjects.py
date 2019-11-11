from models.base import db


HistoricalPersonRelatedObjects = db.Table("historical_person_related_objects", db.metadata,
    db.Column("historical_person_id", db.Integer, db.ForeignKey("historical_person.historical_person_id"),
              nullable=False),
    db.Column("object_id", db.Integer, db.ForeignKey("object.object_id"), nullable=False)
)



