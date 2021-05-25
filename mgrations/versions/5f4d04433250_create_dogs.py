"""create-dogs

Revision ID: 5f4d04433250
Revises: 6f78bde1e9fb
Create Date: 2021-05-21 15:46:18.796907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f4d04433250'
down_revision = '6f78bde1e9fb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'dogs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('name', sa.String),
        sa.Column('breed', sa.String),
        sa.Column('age', sa.Integer),
        sa.Column('size', sa.String),
        sa.Column('description', sa.String)
       
    )


def downgrade():
    op.drop_table('dogs')