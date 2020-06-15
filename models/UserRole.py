from models.base import db


UserRole = db.Table(
    "user_role",
    db.metadata,
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.user_id", ondelete="cascade"),
        primary_key=True,
        nullable=False
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("role.role_id", ondelete="cascade"),
        primary_key=True,
        nullable=False
    )
)
