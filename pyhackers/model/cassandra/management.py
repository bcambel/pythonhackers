from hierachy import *
from cqlengine.management import sync_table, create_keyspace
from cqlengine import connection
#from pyhackers.config import config


def connect():
    connection.setup(['127.0.0.1:9160'])


def create():
    connect()
    create_keyspace('pyhackers')

    sync_table(User)
    sync_table(Post)
    sync_table(Channel)
    sync_table(Project)

    # User related tables
    sync_table(UserTimeLine)
    sync_table(UserFollower)
    sync_table(UserFollowing)
    sync_table(UserPost)

    # Post related Tables
    sync_table(PostComment)
    sync_table(PostFollower)
    sync_table(PostLike)

    # Channel Related Tables
    sync_table(ChannelFollower)
    sync_table(ChannelTimeLine)

    # Project Related
    sync_table(ProjectFollower)
    sync_table(ProjectTimeLine)


def test_insert():

    from datetime import datetime as dt

    User.create(id=1,nick='bcambel',created_at=dt.utcnow(),
                extended={'test':"test"})

    Post.create(orig_id=1,text="Testing")