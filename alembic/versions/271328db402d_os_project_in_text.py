"""os_project in text

Revision ID: 271328db402d
Revises: 2d67c6e370bb
Create Date: 2013-11-30 17:24:08.977556

"""

# revision identifiers, used by Alembic.
revision = '271328db402d'
down_revision = '2d67c6e370bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('os_project', 'description', type_=sa.Text)
    op.alter_column('os_project', 'name', type_=sa.Text)
    op.alter_column('os_project', 'slug', type_=sa.Text)
    op.alter_column('os_project', 'src_url', type_=sa.Text)
    op.alter_column('os_project', 'doc_url', type_=sa.Text)


def downgrade():
    pass
