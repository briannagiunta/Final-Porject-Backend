"""create-matches

Revision ID: 57441b0d742d
Revises: 501fa06131d4
Create Date: 2021-05-21 15:46:43.596331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57441b0d742d'
down_revision = '501fa06131d4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user1_id', sa.Integer),
        sa.Column('user2_id', sa.Integer)
    )


def downgrade():
    op.drop_table('matches')