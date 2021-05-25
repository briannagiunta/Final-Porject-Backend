"""edit-users

Revision ID: 80aa0a7862b1
Revises: 61e338a42e62
Create Date: 2021-05-22 19:30:33.270748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80aa0a7862b1'
down_revision = '61e338a42e62'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('about', sa.String()))


def downgrade():
    op.remove_column('users', sa.Column('about'))
