from models.base import db


class City(db.Model):

    __tablename__ = "city"
    id = db.Column(db.Integer, primary_key=True, name="city_id")
    name = db.Column(db.String(30), name="city_name")
    description = db.Column(db.Text, name="city_description")
