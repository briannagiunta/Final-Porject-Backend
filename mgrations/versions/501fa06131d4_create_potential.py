"""create-potential

Revision ID: 501fa06131d4
Revises: 5f4d04433250
Create Date: 2021-05-21 15:46:35.458370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501fa06131d4'
down_revision = '5f4d04433250'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'potential_matches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user1_id', sa.Integer),
        sa.Column('user2_id', sa.Integer)
    )


def downgrade():
    op.drop_table('potential_matches')
