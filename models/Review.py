import datetime
from models.base import db
from sqlalchemy.orm import relationship


class Review(db.Model):

    __tablename__ = "review"
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        primary_key=True,
        name="user_id",
        nullable=False
    )
    user = relationship("User")
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("entity.entity_id"),
        primary_key=True,
        name="entity_id",
        nullable=False
    )
    entity = relationship("Entity")
    rating = db.Column(db.SMALLINT, name="review_rating", nullable=False)
    time = db.Column(db.DateTime, name="review_time", default=datetime.datetime.utcnow, nullable=False)
    text = db.Column(db.Text, name="review_text")

    def to_json(self):
        return {
            'user': self.user,
            'entity': self.entity_id,
            'time': str(self.time),
            'rating': self.rating,
            'text': str(self.text) if self.text is not None else None
        }
