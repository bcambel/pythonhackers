"""add pypi packages

Revision ID: 32f93e2b03a3
Revises: 127e0d40f05d
Create Date: 2013-12-25 13:57:49.200742

"""

# revision identifiers, used by Alembic.
revision = '32f93e2b03a3'
down_revision = '127e0d40f05d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'package',

        sa.Column('name', sa.Text,primary_key=True, nullable=False,index=True),

        sa.Column('author', sa.Text, nullable=True),
        sa.Column('author_email', sa.Text, nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('url', sa.Text, nullable=True),
        sa.Column('mdown', sa.Integer, nullable=True),
        sa.Column('wdown', sa.Integer, nullable=True),
        sa.Column('ddown', sa.Integer, nullable=True),
        sa.Column('data', sa.Text, nullable=True),
        )

def downgrade():
    op.drop_table("package")
