"""create-users

Revision ID: c86aeacd14fe
Revises: 
Create Date: 2021-05-20 19:16:21.152907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c86aeacd14fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password', sa.String, nullable=False)
    )


def downgrade():
    op.drop_table('users')
