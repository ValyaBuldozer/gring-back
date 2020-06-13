"""Added uniqueness to role name.

Revision ID: 38f5241d3e06
Revises: 444e2014db70
Create Date: 2020-06-09 22:30:34.793591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38f5241d3e06'
down_revision = '444e2014db70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'role', ['role_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'role', type_='unique')
    # ### end Alembic commands ###