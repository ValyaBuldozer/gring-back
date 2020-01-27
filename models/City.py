from models.base import db


class City(db.Model):

    __tablename__ = "city"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="city_id",
        nullable=False)
    name = db.Column(
        db.String(30),
        name="city_name",
        nullable=False)
    image_link = db.Column(
        db.String(250),
        name="city_image_link",
        nullable=False)
    description = db.Column(
        db.Text,
        name="city_description",
        nullable=False)
