"""empty message

Revision ID: 6788a31f6138
Revises: 59503ddea0f0
Create Date: 2020-12-16 20:10:13.316058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6788a31f6138'
down_revision = '59503ddea0f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Shows',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'venue_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Shows')
    # ### end Alembic commands ###
