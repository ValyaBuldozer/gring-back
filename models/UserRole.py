from models.base import db
from sqlalchemy import PrimaryKeyConstraint


UserRole = db.Table("user_role", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), nullable=False),
    db.Column("role_id", db.Integer, db.ForeignKey("role.role_id"), nullable=False)
)
