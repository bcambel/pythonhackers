from cqlengine import BatchQuery
from pyhackers.model.cassandra.hierachy import Story, UserFollower, Feed


class StoryWorker:


    def __init__(self,id=None, actor=None, type=None, target=None):
        self.id = id
        self.actor = actor
        self.type = type
        self.target = target

    def new_story(self):
        Story.create(id=self.id, actor=self.actor, type=self.type, target=self.target)

        followers = self.find_followers()

        with BatchQuery(execute_on_exception=True) as b:
            for follower_id in followers:
                Feed.batch(b).create(story=self.id, user=follower_id,actor=self.actor)

    def find_followers(self):
        user_followers_q = UserFollower.objects.filter(user_id=self.actor).all()
        return [follower.follower_id for follower in user_followers_q]


def create_story(**kwargs):
    StoryWorker(**kwargs).new_story()
