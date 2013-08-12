"""Add parent field to open source projects

Revision ID: 1f27928bf1a6
Revises: 4ee15a6a9f1c
Create Date: 2013-08-12 18:45:10.033955

"""

# revision identifiers, used by Alembic.
revision = '1f27928bf1a6'
down_revision = '4ee15a6a9f1c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('os_project', sa.Column('parent', sa.String(100)))


def downgrade():
    op.drop_column('os_project', 'parent')
