"""add-image-to-users

Revision ID: fe2b6d4f3667
Revises: 80aa0a7862b1
Create Date: 2021-05-24 11:19:20.105601

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe2b6d4f3667'
down_revision = '80aa0a7862b1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('image', sa.String()))


def downgrade():
    op.remove_column('users', sa.Column('image'))