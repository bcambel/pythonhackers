from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, Discussion, DiscussionPost, DiscussionCounter
from pyhackers.service.post import new_post
from pyhackers.utils import markdown_to_html

from slugify import slugify


def load_discussion(slug, id):
    discussion = Discussion.objects.get(id=id)
    disc_posts = [(p.post_id,p.user_id) for p in DiscussionPost.objects.filter(disc_id=id).limit(100)]
    message = Post.objects.get(id=discussion.post_id)

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

    new_post(text, code='', current_user_id=current_user_id, post_id=post_id)

    return disc_id, slug


def new_discussion_message(discussion_id, text, current_user_id):
    discussion = Discussion.objects.get(id=discussion_id)
    discussion.users = discussion.users + list(current_user_id)


    p = Post()
    p.id = idgen_client.get()
    p.discussion_id = discussion_id
    p.text = text
    p.html = markdown_to_html(text)
    p.user_id = current_user_id

    ## Create an entry in the timeline to say that this user
    # has created a post in the given discussion
    # Event.new_post_message

    p.create()

    DiscussionPost.create(disc_id=discussion_id, post_id=p.id, user_id=current_user_id)

    DiscussionCounter.message_count += 1

    return p.id
