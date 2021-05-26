"""create-user-chats

Revision ID: ea2a791ff23e
Revises: e4103dc2dbf5
Create Date: 2021-05-26 13:26:41.693074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea2a791ff23e'
down_revision = 'e4103dc2dbf5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_chats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('chat_id', sa.Integer)
    )


def downgrade():
    op.drop_table('user_chats')