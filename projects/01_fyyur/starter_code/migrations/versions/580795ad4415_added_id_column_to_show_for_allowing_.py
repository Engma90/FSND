"""Added id column to show for allowing duplicates

Revision ID: 580795ad4415
Revises: ca46ae2f4155
Create Date: 2020-12-18 16:12:09.457613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '580795ad4415'
down_revision = 'ca46ae2f4155'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'id')
    # ### end Alembic commands ###
