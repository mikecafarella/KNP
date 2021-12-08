"""add blobs table

Revision ID: f2e710040490
Revises: 3e27ccd50d88
Create Date: 2021-12-08 14:49:13.542363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2e710040490'
down_revision = '3e27ccd50d88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blobs',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('contents', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blobs')
    # ### end Alembic commands ###
