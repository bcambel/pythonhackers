"""add flags to projects

Revision ID: 127e0d40f05d
Revises: b4f4be61aa7
Create Date: 2013-12-22 09:52:38.357986

"""

# revision identifiers, used by Alembic.
revision = '127e0d40f05d'
down_revision = 'b4f4be61aa7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("os_project", sa.Column('hide', sa.Boolean))
    op.add_column("os_project", sa.Column('lang', sa.SmallInteger))


def downgrade():
    op.drop_column("os_project", 'hide')
    op.drop_column("os_project", 'lang')
