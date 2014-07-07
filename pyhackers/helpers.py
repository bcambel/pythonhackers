import logging
import time
from datetime import datetime as dt
from flask import request, render_template as template_render
from flask.ext.login import current_user, AnonymousUserMixin
from json import dumps
import calendar
from pyhackers.config import config
from pyhackers.service.channel import get_channel_list
from pyhackers.service.topic import load_topics_jsonable

purge_key = config.get("app", 'purge_key')
debug = config.get("app", "debug")
PRODUCTION = not (debug in ['True', '1', True, 1])
cache_buster = calendar.timegm(time.gmtime())


def render_base_template(*args, **kwargs):
    try:
        logging.warn(current_user.is_anonymous())
        is_logged = not current_user.is_anonymous()
    except Exception as ex:
        logging.exception(ex)
        is_logged = False

    active_user = current_user.jsonable() if not current_user.is_anonymous() else {}
    user_data = dumps(active_user)
    logging.warn(user_data)

    # FIXME: render_template also contains some of the dict-keys.
    kwargs.update(**{'__v__': int(time.time()),
                     'user': active_user,
                     'user_json': user_data,
                     'topics_json': dumps(load_topics_jsonable()),
                     'channels': get_channel_list(),
                     'PROD': PRODUCTION,
                     'logged_in': bool(is_logged),
                     'year': dt.utcnow().year,
    })

    return render_template(*args, **kwargs)


def render_template(*args, **kwargs):
    """
    Render template for anonymous access with cache_buster,PROD settings, used for caching
    """
    params = {'cache_buster': cache_buster, 'user': {}, 'user_json': {}, 'PROD': PRODUCTION,
                     'static_route': 'http://cdn1.pythonhackers.com'}
    params.update(**kwargs)

    return template_render(*args, **params)


def current_user_id():
    if isinstance(current_user, AnonymousUserMixin):
        return None
    else:
        if hasattr(current_user, 'id'):
            return current_user.id
        else:
            return None