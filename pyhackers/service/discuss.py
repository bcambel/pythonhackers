import logging
from cqlengine.query import DoesNotExist
from pyhackers.events import Event
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, Discussion, DiscussionPost, DiscussionCounter, UserDiscussion, \
    User as CsUser, DiscussionFollower
from pyhackers.service.post import new_post, load_posts
from pyhackers.service.user import load_user_profiles
from pyhackers.utils import markdown_to_html

from slugify import slugify

from datetime import datetime as dt


def load_discussions():
    discussions = Discussion.objects.all().limit(50)

    return discussions


def load_discussions_by_id(ids):
    return Discussion.objects.filter(id__in=ids).limit(50)


def load_discussion(slug, discussion_id, current_user_id=None):
    discussion, disc_posts, users, counters = discussion_messages(discussion_id)

    try:
        message = Post.objects.get(id=discussion.post_id)
    except DoesNotExist:
        message = {}

    followers = [d.user_id for d in DiscussionFollower.objects.filter(disc_id=discussion_id)]
    user = {}

    if current_user_id in followers:
        user = {'id': current_user_id, 'following': True}

    # TODO: Utterly we will place this into a background job (more like log processed counter)
    dc = DiscussionCounter.get(id=discussion_id)
    dc.view_count += 1
    dc.save()

    return discussion, disc_posts, message, counters, user


def discussion_messages(discussion_id, after_message_id=None, limit=100):
    discussion = Discussion.objects.get(id=discussion_id)
    if after_message_id:
        post_filter = DiscussionPost.objects.filter(disc_id=discussion_id,
                                                    post_id__gt=after_message_id)
    else:
        post_filter = DiscussionPost.objects.filter(disc_id=discussion_id)

    #FIXME: Here we only get 100 records right now. No Sorting, paging, nothing. Too bad!
    disc_post_lists = [(p.post_id, p.user_id) for p in post_filter.limit(limit)]
    post_ids = list(set([x[0] for x in disc_post_lists]))
    user_ids = list(set([x[1] for x in disc_post_lists]))
    users = load_user_profiles(user_ids)

    disc_posts = load_posts(post_ids)
    for post in disc_posts:
        u = filter(lambda x: x.id == post.user_id, users)

        post.user = u[0] if u is not None else None

    try:
        counters = DiscussionCounter.get(id=discussion_id)
    except DoesNotExist:
        counters = {'message_count': 1, 'user_count': 1, 'view_count': 0}

    return discussion, disc_posts, users, counters


def new_discussion(title, text, current_user_id=None):
    disc_id = idgen_client.get()
    post_id = idgen_client.get()

    slug = slugify(title)

    d = Discussion()
    d.id = disc_id
    d.post_id = post_id
    d.message_count = 1
    d.title = title
    d.published_at = dt.utcnow()
    d.user_count = 1
    d.users = {current_user_id}
    d.slug = slug

    d.save()

    disc_counter = DiscussionCounter(id=disc_id)
    disc_counter.message_count = 1
    disc_counter.user_count = 1
    disc_counter.view_count = 1
    disc_counter.save()

    UserDiscussion.create(user_id=current_user_id, discussion_id=d.id)

    new_post(text, code='', current_user_id=current_user_id, post_id=post_id)

    return disc_id, slug


def new_discussion_message(discussion_id, text, current_user_id, nick=''):
    logging.warn("DSCSS:[{}]USER:[{}]".format(discussion_id, current_user_id))
    discussion = Discussion.objects.get(id=discussion_id)

    p = Post()
    p.id = idgen_client.get()
    p.discussion_id = discussion_id
    p.text = text
    p.html = markdown_to_html(text)
    p.user_id = current_user_id
    p.user_nick = nick
    ## Create an entry in the timeline to say that this user
    # has created a post in the given discussion
    # Event.new_post_message

    p.save()

    Event.message(current_user_id, p.id, None)

    # FIXME: Move all this part to the JOB WORKER! Speed my friend.

    discussion.last_message = p.id
    discussion.users.union({current_user_id})
    discussion.save()

    UserDiscussion.create(user_id=current_user_id, discussion_id=discussion_id)

    DiscussionPost.create(disc_id=discussion_id, post_id=p.id, user_id=current_user_id)

    disc_counter = DiscussionCounter(id=discussion_id)
    disc_counter.message_count += 1
    disc_counter.save()

    return p.id


def get_user_discussion_by_nick(nick):
    try:
        user = CsUser.filter(nick=nick).first()
    except DoesNotExist, dne:
        user = None

    if user is None:
        return

    discussions = list([d.discussion_id for d in UserDiscussion.objects.filter(user_id=user.id)])

    return user, load_discussions_by_id(discussions)


def new_discussion_follower(discussion_id, current_user_id, nick=None):
    dc = DiscussionCounter.get(id=discussion_id)
    dc.follower_count += 1
    dc.save()

    DiscussionFollower.create(disc_id=discussion_id, user_id=current_user_id)


def remove_discussion_follower(discussion_id, current_user_id):
    try:
        follower = DiscussionFollower.objects.filter(disc_id=discussion_id, user_id=current_user_id).first()
        follower.delete()
        dc = DiscussionCounter.get(id=discussion_id)
        dc.follower_count -= 1
        dc.save()
    except DoesNotExist:
        pass
