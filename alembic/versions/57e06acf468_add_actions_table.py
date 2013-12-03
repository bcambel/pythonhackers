"""add actions table

Revision ID: 57e06acf468
Revises: 2aa06b3e5853
Create Date: 2013-12-03 18:52:50.010772

"""

# revision identifiers, used by Alembic.
revision = '57e06acf468'
down_revision = '2aa06b3e5853'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'action',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('from_id', sa.BigInteger, nullable=False),
        sa.Column('to_id', sa.BigInteger),
        sa.Column('action', sa.SmallInteger, nullable=False),
        sa.Column('created_at', sa.DateTime),
        sa.Column('deleted',sa.Boolean, default=False),
        sa.Column('deleted_at',sa.DateTime),
    )


def downgrade():
    op.drop_table('action')
