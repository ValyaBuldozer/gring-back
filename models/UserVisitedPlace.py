from models.base import db
import datetime


UserVisitedPlace = db.Table(
    "user_visited_place",
    db.metadata,
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.user_id", ondelete="cascade"),
        index=True,
        nullable=False
    ),
    db.Column(
        "place_id",
        db.Integer,
        db.ForeignKey("place.object_id", ondelete="cascade"),
        index=True,
        nullable=False
    ),
    db.Column(
        "add_time",
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
)