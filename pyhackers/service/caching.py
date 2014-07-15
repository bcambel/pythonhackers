from pyhackers.service.discuss import load_discussions_header
import logging
from itertools import chain


class ObjectTypes:
    DISCUSSION = 1
    POST = 2
    USERS = 3


class StupidCache:
    discussions = {}
    posts = {}
    users = {}

    @classmethod
    def resolve(cls, object_type, ids):
        logging.warn("Resolving %s" % ids)
        object_ids = [str(oid) for oid in ids]
        if object_type == ObjectTypes.DISCUSSION:
            missing_ids = list(set(object_ids) - set(StupidCache.discussions.keys()))

            if len(missing_ids) > 0:
                logging.warn("Missing IDS: {}".format(missing_ids))
                discussions = load_discussions_header(missing_ids)
                for disc in discussions:
                    StupidCache.discussions[str(disc.id)] = disc
                    #StupidCache.discussions = dict(chain(StupidCache.discussions.iteritems(), {}.iteritems()))

            return {oid: StupidCache.discussions[oid] for oid in object_ids}


def resolve_discussion_ids(ids):
    return StupidCache.resolve(ObjectTypes.DISCUSSION, ids)

