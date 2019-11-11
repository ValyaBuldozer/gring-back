from models.base import db
from models.WeekDay import WeekDay
from sqlalchemy.orm import relationship


class Timetable(db.Model):

    __tablename__ = "timetable"
    id = db.Column(
        db.Integer, db.ForeignKey("public_place.object_id"), primary_key=True, name="public_place_id", nullable=True
    )
    public_place = relationship("PublicPlace")
    week_day = db.Column(db.Enum(WeekDay), name="week_day", nullable=True)
    open_time = db.Column(db.Time, name="open_time", nullable=True)
    close_time = db.Column(db.Time, name="close_time", nullable=True)