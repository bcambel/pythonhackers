"""create user table

Revision ID: 4ee15a6a9f1c
Revises: None
Create Date: 2013-08-08 21:01:38.192523

"""

# revision identifiers, used by Alembic.
revision = '4ee15a6a9f1c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True,autoincrement=True),
        sa.Column('nick', sa.String(64), unique = True, index=True, nullable=False),
        sa.Column('email', sa.Unicode(200),index = True, unique = True),
    )

    op.create_table(
        'os_project',
        sa.Column('id', sa.Integer, primary_key=True,autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(64), unique = True, index=True, nullable=False),
        sa.Column('description', sa.Unicode(200)),
        sa.Column('src_url', sa.Unicode(200)),
        sa.Column('doc_url', sa.Unicode(200)),
        sa.Column('starts', sa.Integer),
        sa.Column('watchers', sa.Integer),
        sa.Column('forks', sa.Integer),
    )


def downgrade():
    op.drop_table('user')
    op.drop_table('os_project')
