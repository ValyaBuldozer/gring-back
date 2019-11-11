from models.base import db


class User(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, name="user_id", nullable=True)
    name = db.Column(db.String(100), name="user_name", nullable=True)
    password = db.Column(db.String(100), name="user_password", nullable=True)
    email = db.Column(db.String(200), name="user_email", nullable=True)