import logging
from cqlengine.query import DoesNotExist
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, PostVote, PostCounter
from pyhackers.events import Event
from pyhackers.utils import markdown_to_html


def load_posts(post_ids,current_user_id=None):
    """
    Select multiple posts from the service.
    We will definitely need to [mem]Cache these records to do a fast lookup batch query.
    Of course also cache invalidation needs to be considered.
    """
    logging.warn("Ids===={}".format(post_ids))

    # If list is not used, or any call that trigger __iter__ will end up with the query syntax
    # rather than the data itself.
    #posts_query = Post.objects.filter(id__in=post_ids).limit(100).allow_filtering()
    #post_counters = list(PostCounter.objects.filter(id__in=post_ids).limit(100).allow_filtering())

    post_objects = []
    # ok ,
    for post_id in post_ids:
        p = Post.objects.get(id=post_id)

        try:
            pc = PostCounter.objects.get(id=post_id) #filter(lambda x: x.id == post.id, post_counters)
            stats = pc._as_dict()
            del stats['id']
            p.__dict__['statistics'] = stats
        except DoesNotExist, dne:
            pass

        if current_user_id is not None:
            try:
                pv = PostVote.objects.get(post_id=post_id, user_id=current_user_id)
                p.__dict__['upvoted'] = True
            except DoesNotExist, dne:
                pass
        post_objects.append(p)

    return post_objects


def new_post(text, code=None, current_user_id=None, post_id=None, nick=None):
    logging.warn("Post is=>{}".format(post_id))

    html = markdown_to_html(text)

    message = Post()
    message.id = post_id or idgen_client.get()
    message.text = text
    message.html = html
    message.user_id = current_user_id
    message.user_nick = nick
    message.save()

    Event.message(current_user_id, message.id, None)


def upvote_message(message_id, current_user_id=None):
    try:
        Post.objects.get(id=message_id)
    except DoesNotExist, dne:
        return

    try:
        already_vote = PostVote.objects.get(post_id=message_id, user_id=current_user_id)
        if already_vote.posivite:
            return
    except DoesNotExist, dne:
        pass

    PostVote.create(post_id=message_id, user_id=current_user_id, positive=True)

    try:
        pc = PostCounter.objects.get(id=message_id)
    except DoesNotExist, dne:
        pc = PostCounter.create(id=message_id)

    if pc is not None:
        pc.up_votes += 1
        pc.save()

    Event.up_vote(current_user_id,message_id)