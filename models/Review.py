import datetime
from models.base import db
from sqlalchemy.orm import relationship


class Review(db.Model):

    __tablename__ = "review"
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id"), primary_key=True, name="user_id", nullable=False
    )
    user = relationship("User")
    object_id = db.Column(
        db.Integer, db.ForeignKey("object.object_id"), primary_key=True, name="object_id", nullable=False
    )
    object = relationship("Object")
    rating = db.Column(db.SMALLINT, name="review_raiting", nullable=False)
    time = db.Column(db.DateTime, name="review_time", default=datetime.datetime.utcnow, nullable=False)
    text = db.Column(db.Text, name="review_text")

    def to_json(self):
        return {
            'user': self.user,
            'time': str(self.time),
            'raiting': self.rating,
            'text': str(self.text) if self.text is not None else None
        }
