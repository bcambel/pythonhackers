"""add role to User table

Revision ID: 67ea78b2bbd
Revises: 43d4e52bb53f
Create Date: 2013-12-01 06:59:18.813595

"""

# revision identifiers, used by Alembic.
revision = '67ea78b2bbd'
down_revision = '43d4e52bb53f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("user", sa.Column("role", sa.Integer))


def downgrade():
    op.drop_column("user", "role")
