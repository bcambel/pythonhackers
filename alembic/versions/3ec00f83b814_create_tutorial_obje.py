"""create tutorial object

Revision ID: 3ec00f83b814
Revises: 32f93e2b03a3
Create Date: 2014-01-07 18:16:33.130262

"""

# revision identifiers, used by Alembic.
revision = '3ec00f83b814'
down_revision = '32f93e2b03a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'tutorial',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('keywords', sa.Text),
        sa.Column('meta_description', sa.Text),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('content_html', sa.Text),

        sa.Column('slug', sa.Text, index=True, nullable=False),
        sa.Column('upvote_count', sa.Integer),

        sa.Column('created_at', sa.DateTime),
        sa.Column('generated_at', sa.DateTime),

        sa.Column('publish', sa.Boolean, default=True),
        sa.Column('spam', sa.Boolean, default=False),
    )


def downgrade():
    op.drop_table('tutorial')
