from models.base import db


class User(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, name="user_id", nullable=False)
    name = db.Column(db.String(100), name="user_name", nullable=False)
    password = db.Column(db.String(100), name="user_password", nullable=False)
    email = db.Column(db.String(200), name="user_email", nullable=False)