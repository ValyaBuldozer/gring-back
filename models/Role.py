from models.base import db


class Role(db.Model):

    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True, name="role_id", nullable=False)
    name = db.Column(db.String(20), name="role_name", nullable=False)
