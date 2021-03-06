import datetime
from models.base import db
from sqlalchemy.orm import relationship


class Review(db.Model):

    __tablename__ = "review"
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id", ondelete="cascade"),
        primary_key=True,
        name="user_id",
        nullable=False
    )
    user = relationship(
        "User"
    )
    entity_id = db.Column(
        db.Integer,
        db.ForeignKey("entity.entity_id", ondelete="cascade"),
        primary_key=True,
        name="entity_id",
        nullable=False
    )
    entity = relationship(
        "Entity"
    )
    rating = db.Column(
        db.SMALLINT,
        name="review_rating",
        nullable=False
    )
    time = db.Column(
        db.DateTime,
        name="review_last_modified_time",
        default=datetime.datetime.utcnow,
        nullable=False
    )
    text = db.Column(
        db.Text,
        name="review_text",
        nullable=True
    )
    locale = db.Column(
        db.String(2),
        name="review_locale",
        nullable=True
    )

    def to_json(self, locale):
        return {
            'user': self.user,
            'entity': self.entity_id,
            'time': str(self.time),
            'rating': self.rating,
            'text': str(self.text) if self.text is not None else None,
            'locale': self.locale
        }
