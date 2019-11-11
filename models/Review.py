from models.base import db
import datetime

Timetable = db.Table("timetable", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), nullable=False),
    db.Column("object_id", db.Integer, db.ForeignKey("object.object_id"), nullable=False),
    db.Column("review_rating", db.SMALLINT, nullable=False),
    db.Column("review_time", db.DateTime, default=datetime.datetime.utcnow, nullable=False),
    db.Column("review_text", db.Text, nullable=True)
)
