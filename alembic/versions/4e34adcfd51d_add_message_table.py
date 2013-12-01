"""add message table

Revision ID: 4e34adcfd51d
Revises: 67ea78b2bbd
Create Date: 2013-12-01 09:44:30.690886

"""

# revision identifiers, used by Alembic.
revision = '4e34adcfd51d'
down_revision = '67ea78b2bbd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table(
        'message',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('user_nick', sa.String(100)),
        sa.Column('reply_to_id', sa.BigInteger),
        sa.Column('reply_to_uid', sa.Integer),
        sa.Column('reply_to_uname', sa.Unicode(200)),
        sa.Column('ext_id', sa.String),
        sa.Column('ext_reply_id', sa.String),
        sa.Column('slug', sa.Text),
        sa.Column('content', sa.Text),
        sa.Column('content_html', sa.Text),
        sa.Column('lang', sa.String(3)),

        sa.Column('mentions', postgresql.ARRAY(sa.String)),
        sa.Column('urls', postgresql.ARRAY(sa.String)),
        sa.Column('tags', postgresql.ARRAY(sa.String)),
        sa.Column('media', postgresql.ARRAY(sa.String)),

        sa.Column('has_url', sa.Boolean),
        sa.Column('has_channel', sa.Boolean),

        sa.Column('karma', sa.Integer),
        sa.Column('up_votes', sa.Integer),
        sa.Column('down_votes', sa.Integer),
        sa.Column('favorites', sa.Integer),
        sa.Column('published_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('channel_id', sa.Integer),
        sa.Column('channels', postgresql.ARRAY(sa.String)),
        sa.Column('spam', sa.Boolean),
        sa.Column('flagged', sa.Boolean),
        sa.Column('deleted', sa.Boolean),
    )


def downgrade():
    op.drop_table('message')
