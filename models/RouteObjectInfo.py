from models.base import db


RouteObjectInfo = db.Table("route_object_info", db.metadata,
    db.Column("object_id", db.Integer, db.ForeignKey("object.object_id"), nullable=False),
    db.Column("route_id", db.Integer, db.ForeignKey("route.route_id"), nullable=False),
    db.Column("route_object_order", db.Integer, nullable=False),
    db.Column("route_object_description", db.Text),
    db.Column("route_object_audioguide_link", db.String(250))
)


