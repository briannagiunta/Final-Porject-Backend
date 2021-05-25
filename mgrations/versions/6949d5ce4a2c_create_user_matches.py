"""create-user-matches

Revision ID: 6949d5ce4a2c
Revises: 57441b0d742d
Create Date: 2021-05-21 15:46:50.327482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6949d5ce4a2c'
down_revision = '57441b0d742d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_matches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('match_id', sa.Integer)
    )


def downgrade():
    op.drop_table('user_matches')