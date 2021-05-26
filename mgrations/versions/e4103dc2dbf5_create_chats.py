"""create-chats

Revision ID: e4103dc2dbf5
Revises: fe2b6d4f3667
Create Date: 2021-05-26 13:26:29.503342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4103dc2dbf5'
down_revision = 'fe2b6d4f3667'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user1_id', sa.Integer),
        sa.Column('user2_id', sa.Integer)
    )


def downgrade():
    op.drop_table('chats')