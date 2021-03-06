"""Historical person related object rename.

Revision ID: 1d24cba19e40
Revises: 6490c7e8148e
Create Date: 2020-06-17 21:26:00.626118

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from models.HistoricalPersonRelatedObject import HistoricalPersonRelatedObject

# revision identifiers, used by Alembic.
revision = '1d24cba19e40'
down_revision = '6490c7e8148e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historical_person_related_object',
    sa.Column('historical_person_id', sa.Integer(), nullable=False),
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['historical_person_id'], ['historical_person.object_id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['object_id'], ['object.object_id'], ondelete='cascade')
    )

    conn = op.get_bind()
    query = 'select {0} from {1}'.format('historical_person_id, object_id', 'historical_person_related_objects')
    res = conn.execute(query)
    update = []
    for columns in res:
        update.append({
            'historical_person_id': columns[0],
            'object_id': columns[1],
        })
    op.bulk_insert(HistoricalPersonRelatedObject, update)

    op.drop_table('historical_person_related_objects')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historical_person_related_objects',
    sa.Column('historical_person_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('object_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['historical_person_id'], ['historical_person.object_id'], name='historical_person_related_objects_ibfk_1', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['object_id'], ['object.object_id'], name='historical_person_related_objects_ibfk_2', ondelete='CASCADE'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('historical_person_related_object')
    # ### end Alembic commands ###
