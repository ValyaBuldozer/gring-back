from models.base import db


HistoricalPersonRelatedObject = db.Table(
    "historical_person_related_object",
    db.metadata,
    db.Column(
        "historical_person_id",
        db.Integer,
        db.ForeignKey("historical_person.object_id", ondelete="cascade"),
        nullable=False
    ),
    db.Column(
        "object_id",
        db.Integer,
        db.ForeignKey("object.object_id", ondelete="cascade"),
        nullable=False
    )
)
