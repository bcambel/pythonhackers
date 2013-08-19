"""Upgrade for social information

Revision ID: 2d67c6e370bb
Revises: 1f27928bf1a6
Create Date: 2013-08-18 11:37:33.445584

"""

# revision identifiers, used by Alembic.
revision = '2d67c6e370bb'
down_revision = '1f27928bf1a6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """


    """
    op.add_column('user', sa.Column('password', sa.String(120), nullable=True))
    op.add_column('user', sa.Column('first_name', sa.String(80), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(120), nullable=True))
    op.add_column('user', sa.Column('loc', sa.String(50), nullable=True))

    op.add_column('user', sa.Column('follower_count', sa.Integer, nullable=True))
    op.add_column('user', sa.Column('following_count', sa.Integer, nullable=True))

    op.add_column('user', sa.Column('lang', sa.String(5), nullable=True))
    op.add_column('user', sa.Column('pic_url', sa.String(200), nullable=True))

    op.create_table(
        'social_user',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('acc_type', sa.String(2), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.Unicode(200), index=True),
        sa.Column('nick', sa.Unicode(64), index=True,),
        sa.Column('follower_count', sa.Integer),
        sa.Column('following_count', sa.Integer),
        sa.Column('ext_id', sa.String(50)),
        sa.Column('access_token', sa.String(100)),
        sa.Column('hireable', sa.Boolean),
    )


def downgrade():
    op.drop_column('user', 'password')
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'loc')

    op.drop_column('user', 'follower_count')
    op.drop_column('user', 'following_count')

    op.drop_column('user', 'lang')
    op.drop_column('user', 'pic_url')

    op.drop_table("social_user")

