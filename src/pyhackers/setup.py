import memcache
from simplekv.memory.memcachestore import MemcacheStore
from flaskext.kvsession import KVSessionExtension
from flask.ext.login import LoginManager
from config import config

login_manager = LoginManager()
login_manager.session_protection = "strong"

mc = memcache.Client([config.get('app', 'mc')],
                     debug=int(config.get('app', 'mc_debug')))


def setup_application_extensions(app, login_view='/login'):
    store = MemcacheStore(mc)

    KVSessionExtension(store, app)
    login_manager.login_view = login_view
    login_manager.init_app(app)