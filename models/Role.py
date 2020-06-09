from models.base import db
from models.RoleName import RoleName


class Role(db.Model):

    __tablename__ = "role"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="role_id",
        nullable=False
    )
    name = db.Column(
        db.Enum(RoleName),
        name="role_name",
        nullable=False,
        unique=True
    )
