"""Foreign keys nullable rework.

Revision ID: 8fd20aa77942
Revises: 38f5241d3e06
Create Date: 2020-06-13 15:42:35.369212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fd20aa77942'
down_revision = '38f5241d3e06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('historical_person_ibfk_3', 'historical_person', type_='foreignkey')
    op.create_foreign_key(None, 'historical_person', 'locale_string', ['person_patronymic_id'], ['string_id'], ondelete='SET NULL')
    op.drop_constraint('object_ibfk_1', 'object', type_='foreignkey')
    op.create_foreign_key(None, 'object', 'locale_link', ['object_audioguide_link_id'], ['link_id'], ondelete='SET NULL')
    op.drop_constraint('public_place_ibfk_3', 'public_place', type_='foreignkey')
    op.drop_constraint('public_place_ibfk_2', 'public_place', type_='foreignkey')
    op.create_foreign_key(None, 'public_place', 'locale_string', ['public_place_visit_cost_id'], ['string_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'public_place', 'locale_string', ['public_place_avg_bill_id'], ['string_id'], ondelete='SET NULL')
    op.drop_constraint('route_place_info_ibfk_3', 'route_place_info', type_='foreignkey')
    op.drop_constraint('route_place_info_ibfk_4', 'route_place_info', type_='foreignkey')
    op.create_foreign_key(None, 'route_place_info', 'locale_link', ['route_place_audioguide_link_id'], ['link_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'route_place_info', 'locale_string', ['route_place_description_id'], ['string_id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'route_place_info', type_='foreignkey')
    op.drop_constraint(None, 'route_place_info', type_='foreignkey')
    op.create_foreign_key('route_place_info_ibfk_4', 'route_place_info', 'locale_string', ['route_place_description_id'], ['string_id'])
    op.create_foreign_key('route_place_info_ibfk_3', 'route_place_info', 'locale_link', ['route_place_audioguide_link_id'], ['link_id'])
    op.drop_constraint(None, 'public_place', type_='foreignkey')
    op.drop_constraint(None, 'public_place', type_='foreignkey')
    op.create_foreign_key('public_place_ibfk_2', 'public_place', 'locale_string', ['public_place_avg_bill_id'], ['string_id'])
    op.create_foreign_key('public_place_ibfk_3', 'public_place', 'locale_string', ['public_place_visit_cost_id'], ['string_id'])
    op.drop_constraint(None, 'object', type_='foreignkey')
    op.create_foreign_key('object_ibfk_1', 'object', 'locale_link', ['object_audioguide_link_id'], ['link_id'])
    op.drop_constraint(None, 'historical_person', type_='foreignkey')
    op.create_foreign_key('historical_person_ibfk_3', 'historical_person', 'locale_string', ['person_patronymic_id'], ['string_id'])
    # ### end Alembic commands ###
