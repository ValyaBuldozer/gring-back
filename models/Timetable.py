from models.base import db
from models.WeekDay import WeekDay
from sqlalchemy.orm import relationship


class Timetable(db.Model):

    __tablename__ = "timetable"
    id = db.Column(
        db.Integer,
        db.ForeignKey("public_place.object_id"),
        primary_key=True,
        name="public_place_id",
        nullable=False
    )
    public_place = relationship(
        "PublicPlace"
    )
    week_day = db.Column(
        db.Enum(WeekDay),
        name="week_day",
        nullable=False,
        primary_key=True)
    open_time = db.Column(
        db.Time,
        name="open_time",
        nullable=False)
    close_time = db.Column(
        db.Time,
        name="close_time",
        nullable=False)

    def to_json(self):
        return {
            'day': self.week_day.name,
            'openTime': str(self.open_time),
            'closeTime': str(self.close_time)
        }
