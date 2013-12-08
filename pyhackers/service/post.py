import logging
from pyhackers.db import DB as db
from pyhackers.model.message import Message
from pyhackers.model.cassandra.hierachy import (
    User as CsUser, Post as CsPost, UserPost as CsUserPost)


def new_post(message, code, current_user):
    m = Message()
    m.user_id = current_user.id
    m.user_nick = current_user.nick
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
        post = CsPost.create(orig_id=m.id, text=message)
        post_id = post.id

        CsUserPost.create(user_id=current_user.id, post_id=post_id)
    else:
        logging.warn("Misery sinks in...")

        # Push the post to all of the User's Followers