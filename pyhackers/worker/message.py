import logging
from cqlengine.query import DoesNotExist
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import (
    User as CsUser, Post as CsPost, UserPost as CsUserPost, UserFollower as CsUserFollower,
    UserTimeLine, UserCounter, Story, StoryTypes, Feed)

from pyhackers.util.textractor import Parser

parser = Parser()


class MessageWorker():
    def __init__(self, user, message, context, **kwargs):
        self.user_id = user
        self.message_id = message
        self.context = context
        self.user = None
        self.message = None
        self.message_text = ''
        self.kwargs = kwargs

    def resolve(self):
        self.user = CsUser.objects.get(id=self.user_id)
        self.message = CsPost.objects.get(id=self.message_id)
        self.message_text = parser.parse(self.message.text)

        logging.warn("Process {}".format(self.message))

    def create_cassandra_objects(self):
        logging.warn("Process: Message=>{}".format(self.message.id))

        post_id = self.message_id
        story_id = idgen_client.get()

        CsUserPost.create(user_id=self.user_id, post_id=post_id)
        Story.create(id=story_id, actor=self.user_id, type=StoryTypes.POST, target=self.message_id)
        user_followers_q = CsUserFollower.objects.filter(user_id=self.user_id).all()

        self.distribute_messages(user_followers_q, post_id, story_id)
        self.update_counts()

    def update_counts(self):
        """Update user related counters"""
        # TODO: Exception Handle, create if not found. Move to separate
        try:
            user_counter = UserCounter.objects.get(id=self.user_id)
        except DoesNotExist:
            user_counter = UserCounter.create(id=self.user_id)

        user_counter.messages += 1
        user_counter.save()

    def distribute_messages(self, user_followers_q, post_id, story_id):
        """
        Pushing into the follower's stream
        big guys do it in batch ( 500 followers or so ) we are brave for now.
        once we have huge number of followers, we will keep thinking.
        """
        count = 0

        for follower in user_followers_q:
            UserTimeLine.create(user_id=follower.follower_id, post_id=post_id)
            Feed.create(user=follower.follower_id, actor=self.user_id, story=story_id)
            count += 1

        logging.warn("Message [{}-{}] distributed to {} followers".format(self.message_id, post_id, count))

    def index(self):
        logging.warn("Index...{}".format(self.message))

    def url_rewrite(self):
        logging.warn("URL Rewrite..{}".format(self.message))

    def wait(self):
        logging.warn("Long running thing..")
        logging.warn("=" * 40)

    def run(self):
        self.resolve()
        self.create_cassandra_objects()
        self.index()
        self.url_rewrite()
        self.wait()


def new_message_worker(user, message, context, **kwargs):
    logging.warn("[WORKER][FOO] {} - {} - {}".format(user, message, context))
    MessageWorker(user, message, context, **kwargs).run()