from sqlalchemy import desc

from models.Role import Role
from models.base import db
from models.UserFavoritePlace import UserFavoritePlace
from sqlalchemy.orm import relationship
from models.base import get_session


class User(db.Model):

    __tablename__ = "user"
    id = db.Column(
        db.Integer,
        primary_key=True,
        name="user_id",
        nullable=False
    )
    name = db.Column(
        db.String(100),
        name="user_name",
        nullable=False
    )
    password = db.Column(
        db.String(100),
        name="user_password",
        nullable=False
    )
    email = db.Column(
        db.String(200),
        name="user_email",
        nullable=False
    )
    roles = relationship(
        "Role",
        secondary="user_role",
        single_parent=True,
        backref=db.backref('user')
    )
    favorite_places = relationship(
        "Place",
        secondary="user_favorite_place",
        single_parent=True,
        order_by=desc(UserFavoritePlace.c.add_time),
        backref=db.backref('user')
    )

    def can(self, allowed_roles):
        user_role_ids = []
        for role in self.roles:
            user_role_ids.append(role.id)
        for allowed_role in allowed_roles:
            if allowed_role.value not in user_role_ids:
                return False

        return True

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }
