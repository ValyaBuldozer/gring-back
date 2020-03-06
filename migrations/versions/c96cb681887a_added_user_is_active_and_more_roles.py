"""Added user.is_active and more roles.

Revision ID: c96cb681887a
Revises: cb398cf84fc1
Create Date: 2020-02-27 20:19:22.360836

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c96cb681887a'
down_revision = 'cb398cf84fc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('role', 'role_name',
               existing_type=mysql.ENUM('admin', 'moder', 'user'),
               type_=sa.Enum('admin', 'content_moder', 'user_moder', 'user', name='rolename'),
               existing_nullable=False)
    op.add_column('user', sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_active')
    op.alter_column('role', 'role_name',
               existing_type=sa.Enum('admin', 'content_moder', 'user_moder', 'user', name='rolename'),
               type_=mysql.ENUM('admin', 'moder', 'user'),
               existing_nullable=False)
    # ### end Alembic commands ###