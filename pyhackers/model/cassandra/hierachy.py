import uuid
from cqlengine import columns
from cqlengine.models import Model
from datetime import datetime as dt

class MBase(Model):
    __abstract__ = True
    __keyspace__ = 'pyhackers'


class Post(MBase):
    id = columns.TimeUUID(primary_key=True, default=uuid.uuid1)
    orig_id = columns.BigInt(index=True)
    text = columns.Text(required=True)
    likes = columns.Counter


class Project(MBase):
    id = columns.Integer(primary_key=True)
    follower_count = columns.Counter


class Channel(MBase):
    id = columns.Integer(primary_key=True)


class User(MBase):
    id = columns.Integer(primary_key=True)
    nick = columns.Text(required=True, index=True)
    created_at = columns.DateTime(default=dt.utcnow())
    follower_count = columns.Counter
    following_count = columns.Counter
    extended = columns.Map(columns.Text, columns.Text)


class UserTimeLine(MBase):
    user_id = columns.Integer(primary_key=True)
    post_id = columns.TimeUUID(primary_key=True)


class UserPost(MBase):
    user_id = columns.Integer(primary_key=True)
    post_id = columns.TimeUUID(primary_key=True)


class UserFollower(MBase):
    user_id = columns.Integer(primary_key=True)
    follower_id = columns.Integer(primary_key=True)


class UserFollowing(MBase):
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
    post_id = columns.TimeUUID(primary_key=True)


class ProjectTimeLine(MBase):
    project_id = columns.Integer(primary_key=True)
    post_id = columns.TimeUUID(primary_key=True)


class PostLike(MBase):
    post_id = columns.TimeUUID(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class PostComment(MBase):
    post_id = columns.TimeUUID(primary_key=True)
    comment_id = columns.TimeUUID(primary_key=True)

from management import connect

connect()