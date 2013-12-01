
from flask.ext.cache import Cache


def init(app):
    global cache
    cache = Cache(app, config={'CACHE_TYPE': 'memcached'})
    cache.init_app(app)
