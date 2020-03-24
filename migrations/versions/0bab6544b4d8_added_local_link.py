"""Added local link.

Revision ID: 0bab6544b4d8
Revises: ea5ad7587c7f
Create Date: 2020-03-20 17:11:05.920076

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
from migrations.util.localize_table import localize_two_id_table, localize_one_id_table
from models.LocaleLink import LocaleLink
from models.Object import Object
from models.RoutePlaceInfo import RoutePlaceInfo

revision = '0bab6544b4d8'
down_revision = 'ea5ad7587c7f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locale_link',
    sa.Column('link_id', sa.String(length=36), nullable=False),
    sa.Column('link_locale', sa.Enum('ru', 'en', name='language'), nullable=False),
    sa.Column('link_path', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('link_id', 'link_locale')
    )

    op.add_column('object', sa.Column('object_audioguide_link_id', sa.String(length=36), nullable=True))
    locale_update = localize_one_id_table(
        conn=conn,
        table=Object.__table__,
        id_col_name='object_id',
        text_col_names=['object_audioguide_link'],
        local_type='link'
    )
    op.bulk_insert(LocaleLink.__table__, locale_update)
    op.create_foreign_key(None, 'object', 'locale_link', ['object_audioguide_link_id'], ['link_id'])
    op.drop_column('object', 'object_audioguide_link')

    op.add_column('route_place_info', sa.Column('route_place_audioguide_link_id', sa.String(length=36), nullable=True))
    locale_update = localize_two_id_table(
        conn=conn,
        table=RoutePlaceInfo.__table__,
        col_id_names=['place_id', 'route_id'],
        text_col_names=['route_place_audioguide_link'],
        local_type='link'
    )
    op.bulk_insert(LocaleLink.__table__, locale_update)
    op.create_foreign_key(None, 'route_place_info', 'locale_link', ['route_place_audioguide_link_id'], ['link_id'])
    op.drop_column('route_place_info', 'route_place_audioguide_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('route_place_info', sa.Column('route_place_audioguide_link', mysql.VARCHAR(length=250), nullable=True))
    op.drop_constraint(None, 'route_place_info', type_='foreignkey')
    op.drop_column('route_place_info', 'route_place_audioguide_link_id')
    op.add_column('object', sa.Column('object_audioguide_link', mysql.VARCHAR(length=250), nullable=True))
    op.drop_constraint(None, 'object', type_='foreignkey')
    op.drop_column('object', 'object_audioguide_link_id')
    op.drop_table('locale_link')
    # ### end Alembic commands ###