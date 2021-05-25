"""edit-users

Revision ID: 6f78bde1e9fb
Revises: c86aeacd14fe
Create Date: 2021-05-21 15:13:48.527901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f78bde1e9fb'
down_revision = 'c86aeacd14fe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('zip', sa.String()))


def downgrade():
    op.remove_column('users', sa.Column('zip'))
