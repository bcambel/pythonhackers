import logging
from pyhackers.db import DB as db
from pyhackers.idgen import idgen_client
from pyhackers.model.message import Message
from pyhackers.events import Event


def new_post(message, code=None, current_user_id=None, post_id=None, user_nick=None):
    m = Message()
    m.id = post_id or idgen_client.get()
    m.user_id = current_user_id
    m.user_nick = user_nick
    m.content = message
    m.content_html = code

    db.session.add(m)
    success = False

    try:
        db.session.commit()
        success = True
    except Exception, ex:
        logging.error(ex)

    if success:
        Event.message(current_user_id, m.id, None)

    else:
        logging.warn("Misery sinks in...")

        # Push the post to all of the User's Followers