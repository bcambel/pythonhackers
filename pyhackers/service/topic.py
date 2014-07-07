import logging
from cqlengine.query import DoesNotExist
from pyhackers.model.cassandra.hierachy import Topic, TopicDiscussion, TopicCounter

topic_cache = {}


def cache_topics(topic_list):

    for t in topic_list:
        topic_cache[t.slug] = t

def topic_slug_to_id(slug):
    topic = topic_cache.get(slug,None)

    if topic is None:
        return 0
    else:
        return topic.id

def load_topics():

    topics = Topic.objects.all()

    topic_list = [t for t in topics]
    cache_topics(topic_list)

    return topic_list


def load_topics_jsonable():
    topics = Topic.objects.all()

    return [t.to_dict() for t in topics]

