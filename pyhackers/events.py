from pyhackers.worker.message import new_message_worker
from pyhackers.job_scheduler import worker_queue as q


class Event:

    @classmethod
    def new_user(cls, user):
        """A user is registered"""
        pass

    @classmethod
    def follow_user(cls, user, following):
        """A user followed another user"""
        pass

    @classmethod
    def message(cls, user, message, context, **kwargs):
        """A user sent a message"""
        q.enqueue(new_message_worker, args=(user, message, context), result_ttl=0)
        pass

    @classmethod
    def follow_project(cls, user, project):
        """A user started to follow a project"""
        pass

    @classmethod
    def discussion(cls, user, discussion):
        """A User started a discussion"""
        pass

    @classmethod
    def reply(cls, user, context, message, reply_message):
        """A user replied to another user within a context ( e.g in a discussion )"""
        pass

    @classmethod
    def up_vote(cls, user, message):
        """A User up-voted a message(or discussion)"""
        pass

    @classmethod
    def user_view(cls, user, profile):
        """A User viewing another user's profile"""
        pass

    @classmethod
    def user_project_view(cls, user, project):
        """A User viewing a project"""
        pass

    @classmethod
    def click(cls, user, link):
        """A user clicked an external link"""
        pass

    @classmethod
    def mention(cls, user, message, mentioned):
        """ A user mentions somebody"""
        pass

    @classmethod
    def share_link(cls, user, link):
        """A user shared a link"""

    @classmethod
    def discussion_view(cls, current_user_id, discussion_id):
        pass
        #dc = DiscussionCounter.get(id=discussion_id)
        #dc.view_count += 1
        #dc.save()

# { type: FollowUser, user: { id: 3 }, target: { type: user, id : 4 } }
# { type: FollowProject, user: { id: 3 }, target: { type: project, id : 5 } }
# { type: FollowChannel, user: { id: 3 }, target: { type: channel, id : 5 } }
# { type: NewMessage, user: { id: 3 }, target: { type: message, id : 5 } }
# { type: NewChannelMessage, user: { id: 3 }, target: { type: project, id : 5 } }
# { type: NewDiscussion, user: { id: 3 }, target: { type: discussion, id : 5 } }
# { type: DiscussionComment, user: { id: 3 }, discussion: { id: 1020 } target: { type: message, id : 5 } }
