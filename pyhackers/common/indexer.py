import logging
from pyes import *
from pyes.exceptions import ElasticSearchException
from pyhackers.sentry import sentry_client

conn = ES('http://es.pythonhackers.com')


def index_data(data, index='sweet', doc='post', id=None):
    logging.warn("Indexing data %s" % (id if id is not None else ""))
    try:
        res = conn.index(data, index, doc, id=id)
    except ElasticSearchException:
        sentry_client.captureException()
        return False

    id = None

    if res is not None:
        id = res.get("_id", None)

    return id, res