"""add category to projects

Revision ID: 43d4e52bb53f
Revises: 271328db402d
Create Date: 2013-12-01 06:41:46.068494

"""

# revision identifiers, used by Alembic.
revision = '43d4e52bb53f'
down_revision = '271328db402d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column("os_project", sa.Column('categories', postgresql.ARRAY(sa.String)))


def downgrade():
    op.drop_column("os_project", 'categories')
