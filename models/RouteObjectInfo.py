from models.base import db


RouteObjectInfo = db.Table("route_object_info", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), nullable=False),
    db.Column("role_id", db.Integer, db.ForeignKey("role.role_id"), nullable=False),
    db.Column("route_object_order", db.Integer, nullable=False),
    db.Column("route_object_description", db.Column(db.Text)),
    db.Column("route_object_audioguide_link", db.Column(db.String(250)))
)


