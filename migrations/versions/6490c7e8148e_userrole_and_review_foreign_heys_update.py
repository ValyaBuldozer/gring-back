"""UserRole and Review  foreign heys update.

Revision ID: 6490c7e8148e
Revises: 8fd20aa77942
Create Date: 2020-06-15 05:45:46.574771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6490c7e8148e'
down_revision = '8fd20aa77942'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('review_ibfk_1', 'review', type_='foreignkey')
    op.drop_constraint('review_ibfk_2', 'review', type_='foreignkey')
    op.create_foreign_key(None, 'review', 'entity', ['entity_id'], ['entity_id'], ondelete='cascade')
    op.create_foreign_key(None, 'review', 'user', ['user_id'], ['user_id'], ondelete='cascade')
    op.drop_constraint('user_role_ibfk_2', 'user_role', type_='foreignkey')
    op.drop_constraint('user_role_ibfk_1', 'user_role', type_='foreignkey')
    op.create_foreign_key(None, 'user_role', 'user', ['user_id'], ['user_id'], ondelete='cascade')
    op.create_foreign_key(None, 'user_role', 'role', ['role_id'], ['role_id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_role', type_='foreignkey')
    op.drop_constraint(None, 'user_role', type_='foreignkey')
    op.create_foreign_key('user_role_ibfk_1', 'user_role', 'role', ['role_id'], ['role_id'])
    op.create_foreign_key('user_role_ibfk_2', 'user_role', 'user', ['user_id'], ['user_id'])
    op.drop_constraint(None, 'review', type_='foreignkey')
    op.drop_constraint(None, 'review', type_='foreignkey')
    op.create_foreign_key('review_ibfk_2', 'review', 'user', ['user_id'], ['user_id'])
    op.create_foreign_key('review_ibfk_1', 'review', 'entity', ['entity_id'], ['entity_id'])
    # ### end Alembic commands ###
