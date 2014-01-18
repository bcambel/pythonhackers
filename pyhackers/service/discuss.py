import logging
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, Discussion, DiscussionPost, DiscussionCounter
from pyhackers.service.post import new_post, load_posts
from pyhackers.service.user import load_user, load_user_profiles
from pyhackers.utils import markdown_to_html

from slugify import slugify


def load_discussion(slug, discussion_id):
    discussion, disc_posts, users, counters = discussion_messages(discussion_id)
    message = Post.objects.get(id=discussion.post_id)


    return discussion, disc_posts, message, counters


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
    counters = DiscussionCounter.get(id=discussion_id)

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
    d.user_count = 1
    d.users = {current_user_id}
    d.slug = slug

    d.save()

    disc_counter = DiscussionCounter.create(id=disc_id)
    disc_counter.message_count = 1
    disc_counter.user_count = 1
    disc_counter.view_count = 1
    disc_counter.save()

    new_post(text, code='', current_user_id=current_user_id, post_id=post_id)

    return disc_id, slug


def new_discussion_message(discussion_id, text, current_user_id):
    logging.warn("DSCSS:[{}]USER:[{}]".format(discussion_id, current_user_id))
    discussion = Discussion.objects.get(id=discussion_id)



    p = Post()
    p.id = idgen_client.get()
    p.discussion_id = discussion_id
    p.text = text
    p.html = markdown_to_html(text)
    p.user_id = current_user_id

    ## Create an entry in the timeline to say that this user
    # has created a post in the given discussion
    # Event.new_post_message

    p.save()

    discussion.last_message = p.id
    discussion.users.union({current_user_id})
    discussion.save()

    DiscussionPost.create(disc_id=discussion_id, post_id=p.id, user_id=current_user_id)
    disc_counter = DiscussionCounter.create(id=discussion_id )
    disc_counter.message_count += 1
    disc_counter.save()

    return p.id
