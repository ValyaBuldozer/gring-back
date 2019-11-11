from models.base import db


class Route(db.Model):

    __tablename__ = "route"
    id = db.Column(db.Integer, primary_key=True, name="route_id", nullable=True)
    name = db.Column(db.String(100), name="route_name", nullable=True)
    description = db.Column(db.Text, name="route_description", nullable=True)