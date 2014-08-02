from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Story, StoryTypes
from pyhackers.worker.message import new_message_worker
from pyhackers.job_scheduler import worker_queue as q
from pyhackers.worker.story import create_story


class Event:

    @classmethod
    def new_user(cls, user):
        """A user is registered"""
        Story.create(id=idgen_client.get(), actor=user.id, type=StoryTypes.JOIN)
        pass

    @classmethod
    def follow_user(cls, user, following):
        """A user followed another user"""
        following_id = following
        create_story(id=idgen_client.get(), actor=user.id, type=StoryTypes.FOLLOW, target=following_id)
        # fetch all the followers of the actors.
        # Let them know that our actor started to follow somebody.

    @classmethod
    def message(cls, user, message, context, **kwargs):
        """A user sent a message"""
        q.enqueue(new_message_worker, args=(user, message, context), result_ttl=0)

    @classmethod
    def follow_project(cls, user, project):
        """A user started to follow a project"""
        create_story(id=idgen_client.get(), actor=user.id, type=StoryTypes.STAR, target=project)

    @classmethod
    def discussion(cls, user, discussion):
        """A User started a discussion"""
        discussion_id = discussion
        create_story(id=idgen_client.get(), actor=user.id, type=StoryTypes.DISCUSS, target=discussion_id)

    @classmethod
    def reply(cls, user, context, message, reply_message):
        """A user replied to another user within a context ( e.g in a discussion )"""
        pass

    @classmethod
    def up_vote(cls, user, message):
        """A User up-voted a message(or discussion)"""
        message_id = message
        user_id = user
        create_story(id=idgen_client.get(), actor=user_id, type=StoryTypes.UP_VOTE, target=message_id)
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
        # better to do it via hadoop in the future.
        pass
        #dc = DiscussionCounter.get(id=discussion_id)
        #dc.view_count += 1
        #dc.save()