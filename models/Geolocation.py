from models.base import db


class Geolocation(db.Model):

    __tablename__ = "geolocation"
    id = db.Column(db.Integer, primary_key=True, name="geolocation_id", nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), name="latitude", nullable=False)
    longtude = db.Column(db.DECIMAL(11, 8), name="longtude", nullable=False)
