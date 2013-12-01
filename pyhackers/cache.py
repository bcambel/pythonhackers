
from flask.ext.cache import Cache

cache = None


def init(app):
    global cache
    cache = Cache(app, config={'CACHE_TYPE': 'memcached'})
    cache.init_app(app)
