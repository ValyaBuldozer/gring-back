import datetime
from models.base import db
from sqlalchemy.orm import relationship
from models.User import User
from models.PublicPlace import PublicPlace


class Timetable(db.Model):

    __tablename__ = "timetable"
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id"), primary_key=True, name="user_id", nullable=False
    )
    user = relationship("User")
    user_id = db.Column(
        db.Integer, db.ForeignKey("public_place.object_id"), primary_key=True, name="object_id", nullable=False
    )
    public_place = relationship("PublicPlace")
    rating = db.Column(db.SMALLINT, name="review_rating", nullable=False)
    time = db.Column(db.DateTime, name="review_time", default=datetime.datetime.utcnow, nullable=False)
    text = db.Column(db.Text, name="review_text")