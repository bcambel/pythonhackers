"""add channel table

Revision ID: 2aa06b3e5853
Revises: 4e34adcfd51d
Create Date: 2013-12-03 18:25:31.708420

"""

# revision identifiers, used by Alembic.
revision = '2aa06b3e5853'
down_revision = '4e34adcfd51d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'channel',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('slug', sa.Text, index=True, unique=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('post_count', sa.Integer),
        sa.Column('disabled', sa.Boolean),
    )


def downgrade():
    op.drop_table('channel')
