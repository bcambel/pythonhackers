import logging
from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, Discussion, DiscussionPost, DiscussionCounter
from pyhackers.service.post import new_post, load_posts
from pyhackers.utils import markdown_to_html

from slugify import slugify


def load_discussion(slug, id):
    discussion = Discussion.objects.get(id=id)

    # FIXME: Here we only get 100 records right now. No Sorting, paging, nothing. Too bad!
    disc_post_lists = [(p.post_id, p.user_id) for p in DiscussionPost.objects.filter(disc_id=id).limit(100)]
    message = Post.objects.get(id=discussion.post_id)

    post_ids = [x[0] for x in disc_post_lists]
    user_ids = [x[1] for x in disc_post_lists]

    disc_posts = load_posts(post_ids)

    return discussion, disc_posts, message


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
    discussion.users.union({current_user_id})


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

    DiscussionPost.create(disc_id=discussion_id, post_id=p.id, user_id=current_user_id)
    disc_counter = DiscussionCounter.create(id=discussion_id )
    disc_counter.message_count += 1
    disc_counter.save()

    return p.id
