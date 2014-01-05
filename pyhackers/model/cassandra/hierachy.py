import uuid
from cqlengine import columns
from cqlengine.models import Model
from datetime import datetime as dt
from pyhackers.config import config

hosts = config.get("cassandra", "host")
keyspace = config.get("cassandra", "keyspace")


class MBase(Model):
    __abstract__ = True
    __keyspace__ = keyspace


class Post(MBase):
    id = columns.BigInt(index=True, primary_key=True)
    user_id = columns.Integer(required=True, index=True)
    text = columns.Text(required=True)
    likes = columns.Counter


class Project(MBase):
    id = columns.Integer(primary_key=True)
    follower_count = columns.Counter


class Channel(MBase):
    id = columns.Integer(primary_key=True)
    slug = columns.Text(required=True, index=True)
    name = columns.Text(required=True)


class User(MBase):
    id = columns.Integer(primary_key=True)
    nick = columns.Text(required=True, index=True)
    follower_count = columns.Counter
    following_count = columns.Counter
    extended = columns.Map(columns.Text, columns.Text)


class UserTimeLine(MBase):
    """
    POSTs that user will see in their timeline
    """
    user_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class UserProject(MBase):
    """
    Projects that user follows
    """
    user_id = columns.Integer(primary_key=True)
    project_id = columns.Integer(primary_key=True)


class UserPost(MBase):
    """
    All the POSTs of a user
    """
    user_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class UserFollower(MBase):
    """
    Followers of a user
    """
    user_id = columns.Integer(primary_key=True)
    follower_id = columns.Integer(primary_key=True)


class UserFollowing(MBase):
    """
    A user follows another user
    """
    user_id = columns.Integer(primary_key=True)
    following_id = columns.Integer(primary_key=True)


class ProjectFollower(MBase):
    project_id = columns.Integer(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class PostFollower(MBase):
    post_id = columns.TimeUUID(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class ChannelFollower(MBase):
    channel_id = columns.Integer(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class ChannelTimeLine(MBase):
    channel_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class ProjectTimeLine(MBase):
    project_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class PostLike(MBase):
    post_id = columns.BigInt(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class PostComment(MBase):
    post_id = columns.BigInt(primary_key=True)
    comment_id = columns.BigInt(primary_key=True)


from management import connect


host_list = hosts.split(",")
#connect(host_list)