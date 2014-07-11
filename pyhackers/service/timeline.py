from pyhackers.service.post import load_posts
from pyhackers.model.cassandra.hierachy import User as CsUser,UserPost
from cqlengine.query import DoesNotExist

def get_user_timeline_by_nick(nick):
    try:
        user = CsUser.filter(nick=nick).first()
    except DoesNotExist, dne:
        user = None

    if user is None:
        return

    posts = [p.post_id for p in UserPost.objects.filter(user_id=user.id).order_by('-post_id').limit(5)]

    return user, reversed(load_posts(posts)or [])
