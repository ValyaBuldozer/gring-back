from models.base import db


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="category_id",
        nullable=False
    )
    name = db.Column(
        db.String(30),
        name="category_name",
        nullable=False
    )

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }
