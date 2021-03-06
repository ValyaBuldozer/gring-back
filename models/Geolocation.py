from models.base import db


class Geolocation(db.Model):

    __tablename__ = "geolocation"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="geolocation_id",
        nullable=False
    )
    latitude = db.Column(
        db.DECIMAL(10, 8),
        name="latitude",
        nullable=False
    )
    longitude = db.Column(
        db.DECIMAL(11, 8),
        name="longitude",
        nullable=False
    )

    def to_json(self, locale):
        return {
            'lat': self.latitude.to_eng_string(),
            'lng': self.longitude.to_eng_string()
        }
