"""edit-dogs

Revision ID: 61e338a42e62
Revises: 6949d5ce4a2c
Create Date: 2021-05-21 16:20:17.370754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61e338a42e62'
down_revision = '6949d5ce4a2c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('dogs', sa.Column('image', sa.String()))


def downgrade():
    op.remove_column('dogs', sa.Column('image'))
