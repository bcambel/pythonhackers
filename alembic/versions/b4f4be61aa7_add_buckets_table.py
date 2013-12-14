"""add buckets table

Revision ID: b4f4be61aa7
Revises: 57e06acf468
Create Date: 2013-12-14 18:22:34.088866

"""

# revision identifiers, used by Alembic.
revision = 'b4f4be61aa7'
down_revision = '57e06acf468'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table(
        'bucket',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('slug', sa.Text, index=True, nullable=False),
        sa.Column('follower_count', sa.Integer),
        sa.Column('projects', postgresql.ARRAY(sa.String)),
        sa.Column('created_at', sa.DateTime),
    )


def downgrade():
    op.drop_table('bucket')
