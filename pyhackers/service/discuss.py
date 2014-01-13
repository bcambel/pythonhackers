from pyhackers.idgen import idgen_client
from pyhackers.model.cassandra.hierachy import Post, Discussion, DiscussionPost
from pyhackers.service.post import new_post

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