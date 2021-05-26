"""create-messages

Revision ID: 825287e6e602
Revises: ea2a791ff23e
Create Date: 2021-05-26 13:26:52.346623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '825287e6e602'
down_revision = 'ea2a791ff23e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('chat_id', sa.Integer),
        sa.Column('content', sa.String)
    )


def downgrade():
    op.drop_table('messages')