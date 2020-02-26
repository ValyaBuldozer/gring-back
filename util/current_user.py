from models.User import User
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)


@jwt_required
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user

