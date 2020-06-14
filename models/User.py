from sqlalchemy import desc

from models.UserVisitedPlace import UserVisitedPlace
from models.RoleName import RoleName
from models.Role import Role
from models.base import db
from models.UserFavorite import UserFavorite
from sqlalchemy.orm import relationship
from util import bcrypt_init


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
    is_active = db.Column(
        db.Boolean,
        name="is_active",
        default=True,
        server_default='1',
        nullable=False
    )
    roles = relationship(
        "Role",
        secondary="user_role",
        single_parent=True,
        backref=db.backref('user')
    )
    favorites = relationship(
        "Entity",
        secondary="user_favorite",
        single_parent=True,
        order_by=desc(UserFavorite.c.add_time),
        backref=db.backref('user_favorites')
    )
    image = db.Column(
        db.String(41),
        name="user_image",
        nullable=False
    )
    visited_places = relationship(
        "Place",
        secondary="user_visited_place",
        single_parent=True,
        order_by=desc(UserVisitedPlace.c.add_time),
        backref=db.backref('user_visited_places')
    )

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt_init.bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt_init.bcrypt.check_password_hash(self.password, value)

    def can(self, allowed_roles):
        user_role_ids = []
        for role in self.roles:
            user_role_ids.append(role.name.value)
        for allowed_role in allowed_roles:
            if allowed_role.value in user_role_ids:
                return True

        return False

    def is_moder(self):
        moder_roles = [RoleName.content_moder.value, RoleName.user_moder.value]
        for role in self.roles:
            if role.name.value in moder_roles:
                return True

        return False

    def is_admin(self):
        for role in self.roles:
            if role.name.value is RoleName.admin.value:
                return True

        return False

    def to_json(self, locale):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image
        }
