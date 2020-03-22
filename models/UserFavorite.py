from models.base import db
import datetime


UserFavorite = db.Table(
    "user_favorite",
    db.metadata,
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.user_id", ondelete="cascade"),
        index=True,
        nullable=False
    ),
    db.Column(
        "entity_id",
        db.Integer,
        db.ForeignKey("entity.entity_id", ondelete="cascade"),
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
