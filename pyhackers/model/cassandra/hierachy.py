import uuid
from cqlengine import columns
from cqlengine.models import Model
from datetime import datetime as dt
import time
from pyhackers.utils import unix_time, format_date, epoch_to_date


class MBase(Model):
    __abstract__ = True
    #__keyspace__ = model_keyspace


class PostCounter(MBase):
    id = columns.BigInt(index=True, primary_key=True)
    up_votes = columns.Counter()
    down_votes = columns.Counter()
    views = columns.Counter()
    karma = columns.Counter()
    replies = columns.Counter()


class Post(MBase):
    id = columns.BigInt(index=True, primary_key=True)
    user_id = columns.Integer(required=True, index=True, partition_key=True)
    # TODO: would be a terrible update if the nick is changed ever.
    user_nick = columns.Text()
    text = columns.Text(required=True)
    html = columns.Text(required=False)

    reply_to_id = columns.BigInt()
    reply_to_uid = columns.Integer()
    reply_to_nick = columns.Text()

    ext_id = columns.Text()

    has_url = columns.Boolean()
    has_channel = columns.Boolean()

    # this post is either linked to a DISCUSSION or
    discussion_id = columns.BigInt()
    # CHANNEL or None
    channel_id = columns.Integer()

    spam = columns.Boolean(default=False)
    flagged = columns.Boolean(default=False)
    deleted = columns.Boolean(default=False)

    stats = columns.Map(columns.Ascii, columns.Integer)

    created_at = columns.BigInt(default=unix_time(dt.utcnow()))

    def to_dict(self):
        return {'id': unicode(self.id),
                'text': self.text,
                'html': self.html,
                'user_id': self.user_id,
                'reply_to_id': self.reply_to_id,
                'reply_to_uid': self.reply_to_uid,
                'reply_to_nick': self.reply_to_nick,
                'discussion_id': self.discussion_id,
                'channel_id': self.channel_id,
                'spam': self.spam,
                'flagged': self.flagged,
                'deleted': self.deleted,
                'published_at': self.created_at,
                'ago': self.ago,
                'user': {'id': self.user_id, 'nick': self.user_nick},
                'stats': self.__dict__.get('statistics', {}),
                'upvoted': self.__dict__.get('upvoted', False),
        }

    @property
    def ago(self):
        if self.created_at is None:
            return "some time ago"
        result = int(int(int(time.time() - self.created_at)) / 60.0)
        abb = "m"

        if result > (60 * 24):
            result /= (60 * 24)
            abb = "d"

        if result > 60:
            result /= 60
            abb = "h"

        return "{}{} ago".format(result, abb)


class Project(MBase):
    id = columns.Integer(primary_key=True)
    name = columns.Text()

    #follower_count = columns.Counter


class TopicCounter(MBase):
    id = columns.Integer(primary_key=True)
    views = columns.Counter()
    discussions = columns.Counter()
    messages = columns.Counter()


class Topic(MBase):
    id = columns.Integer(primary_key=True)
    slug = columns.Text()
    name = columns.Text()
    description = columns.Text()
    last_message_id = columns.BigInt(required=False)
    last_message_time = columns.BigInt(default=unix_time(dt.utcnow()))
    main_topic = columns.Boolean(default=False)
    parent_topic = columns.Integer(required=False)
    subtopics = columns.Set(value_type=columns.Integer)


class TopicDiscussion(MBase):
    topic_id = columns.Integer(primary_key=True, required=False)
    discussion_id = columns.BigInt(primary_key=True, required=False)


class Channel(MBase):
    id = columns.Integer(primary_key=True)
    slug = columns.Text(required=True, index=True)
    name = columns.Text(required=True)


class UserCounter(MBase):
    id = columns.Integer(primary_key=True)
    follower_count = columns.Counter()
    following_count = columns.Counter()
    karma = columns.Counter()
    up_vote_given = columns.Counter()
    up_vote_received = columns.Counter()
    down_vote_given = columns.Counter()
    down_vote_taken = columns.Counter()


class User(MBase):
    id = columns.Integer(primary_key=True)
    nick = columns.Text(required=True, index=True)

    extended = columns.Map(columns.Text, columns.Text)
    registered_at = columns.BigInt(default=unix_time(dt.utcnow()))
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))

    def to_dict(self):
        return {
            'id': self.id,
            'nick': self.nick,
            'properties': self.extended,
        }


class UserDiscussion(MBase):
    user_id = columns.Integer(primary_key=True)
    discussion_id = columns.BigInt(primary_key=True)


class DiscussionCounter(MBase):
    id = columns.BigInt(primary_key=True)
    message_count = columns.Counter()
    user_count = columns.Counter()
    view_count = columns.Counter()
    follower_count = columns.Counter()

    def to_dict(self):
        return {
            'message_count': self.message_count,
            'user_count': self.user_count,
            'view_count': self.view_count,
            'follower_count': self.follower_count,
        }


class Discussion(MBase):
    id = columns.BigInt(primary_key=True)
    title = columns.Text(required=True)
    slug = columns.Text(required=True, index=True)
    user_id = columns.Integer(index=True)
    users = columns.Set(value_type=columns.Integer)
    post_id = columns.BigInt()
    last_message = columns.BigInt()
    published_at = columns.BigInt(default=unix_time(dt.utcnow()))
    topic_id = columns.Integer(required=False)

    def to_dict(self):
        return {
            'id': unicode(self.id),
            'title': self.title,
            'slug': self.slug,
            'user_id': self.user_id,
            'post_id': unicode(self.post_id),
            'last_message': unicode(self.last_message),
            'published_at': epoch_to_date(self.published_at),
            'topic_id': unicode(self.topic_id) if self.topic_id is not None else None,
        }

    @property
    def published_date(self):
        return epoch_to_date(self.published_at*1000)


class DiscussionPost(MBase):
    disc_id = columns.BigInt(primary_key=True)
    post_id = columns.BigInt(primary_key=True)
    user_id = columns.Integer(primary_key=True)


class DiscussionFollower(MBase):
    """
    Users who follows a discussion
    """
    disc_id = columns.BigInt(primary_key=True)
    user_id = columns.Integer(primary_key=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


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
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class UserFollowing(MBase):
    """
    A user follows another user
    """
    user_id = columns.Integer(primary_key=True)
    following_id = columns.Integer(primary_key=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class ProjectFollower(MBase):
    project_id = columns.Integer(primary_key=True)
    user_id = columns.Integer(primary_key=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class PostFollower(MBase):
    post_id = columns.TimeUUID(primary_key=True)
    user_id = columns.Integer(primary_key=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class ChannelFollower(MBase):
    channel_id = columns.Integer(primary_key=True)
    user_id = columns.Integer(primary_key=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class ChannelTimeLine(MBase):
    channel_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class ProjectTimeLine(MBase):
    project_id = columns.Integer(primary_key=True)
    post_id = columns.BigInt(primary_key=True)


class PostVote(MBase):
    post_id = columns.BigInt(primary_key=True, partition_key=True)
    user_id = columns.Integer(primary_key=True)
    positive = columns.Boolean(default=True)
    created_at = columns.BigInt(default=unix_time(dt.utcnow()))


class PostReply(MBase):
    post_id = columns.BigInt(primary_key=True)
    reply_post_id = columns.BigInt(primary_key=True)


class GithubProject(MBase):
    id = columns.Integer(primary_key=True)
    full_name = columns.Text(index=True)
    description = columns.Text()
    homepage = columns.Text()
    fork = columns.Boolean()
    forks_count = columns.Integer()
    language = columns.Text()
    master_branch = columns.Text()
    name = columns.Text()
    network_count = columns.Integer()
    open_issues = columns.Integer()
    url = columns.Text()
    watchers_count = columns.Integer()
    is_py = columns.Boolean()
    owner = columns.Integer()
    hide = columns.Boolean(default=False)


class GithubUser(MBase):
    nick = columns.Text(primary_key=True)
    id = columns.Integer(index=True)
    email = columns.Text()
    followers = columns.Integer()
    following = columns.Integer()
    image = columns.Text()
    blog = columns.Text()
    bio = columns.Text()
    company = columns.Text()
    location = columns.Text()
    name = columns.Text()
    url = columns.Text()
    utype = columns.Text()
    public_gists = columns.Integer()
    public_repos = columns.Integer()
    # Ref user info does not contain all the information.
    full_profile = columns.Boolean(default=True)


class GithubUserList(MBase):
    user = columns.Text(primary_key=True)
    starred = columns.List(value_type=columns.Text)
    following = columns.List(value_type=columns.Text)
    followers = columns.List(value_type=columns.Text)


class GithubEvent(MBase):
    id = columns.BigInt(primary_key=True)
    type = columns.Text()
    actor = columns.Text()
    org = columns.Text()
    repo = columns.Text()
    created_at = columns.Float()
    payload = columns.Text()    