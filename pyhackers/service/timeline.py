import logging
from pyhackers.service.post import load_posts
from pyhackers.service.caching import resolve_discussion_ids
from pyhackers.model.cassandra.hierachy import User as CsUser,UserPost
from cqlengine.query import DoesNotExist


def get_user_timeline_by_nick(nick):
    try:
        user = CsUser.filter(nick=nick).first()
    except DoesNotExist, dne:
        user = None

    if user is None:
        return

    post_ids = [p.post_id for p in UserPost.objects.filter(user_id=user.id).order_by('-post_id').limit(50)]
    posts = load_posts(post_ids)
    discussion_ids = [p.discussion_id for p in posts if p.discussion_id is not None]
    discussion_map = resolve_discussion_ids(discussion_ids)

    logging.warn(discussion_map)

    for p in posts:
        p.discussion_name = ""
        p.discussion_slug = ""

        if p.discussion_id is not None:
            discussion = discussion_map.get(str(p.discussion_id), None)
            if discussion is not None:
                logging.warn("Looking for {}".format(p.discussion_id))
                p.discussion_name = discussion.title
                p.discussion_slug = discussion.slug


    return user, posts
