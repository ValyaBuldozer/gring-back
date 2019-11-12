from models.base import db


CategoryObject = db.Table("category_object", db.metadata,
    db.Column("object_id", db.Integer, db.ForeignKey("object.object_id"), nullable=False),
    db.Column("category_id", db.Integer, db.ForeignKey("category.category_id"), nullable=False)
)

