import logging
from pyhackers.db import DB as db
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post
from pyhackers.model.message import Message
from pyhackers.events import Event
from pyhackers.utils import markdown_to_html


def new_post(text, code=None, current_user_id=None, post_id=None, user_nick=None):
    logging.warn("Post is=>{}".format(post_id))

    html = markdown_to_html(text)


    message = Post()
    message.id = post_id or idgen_client.get()
    message.text = text
    message.html = html
    message.user_id = current_user_id
    message.save()
    Event.message(current_user_id, message.id, None)

    #m = Message()
    #m.id = post_id  #or idgen_client.get()
    #m.user_id = current_user_id
    #m.user_nick = user_nick
    #m.content = message
    #m.content_html = code
    #
    #db.session.add(m)
    #success = False
    #
    #try:
    #    db.session.commit()
    #    success = True
    #except Exception, ex:
    #    logging.error(ex)

    #if success:


    #else:
    #    logging.warn("Misery sinks in...")

        # Push the post to all of the User's Followers