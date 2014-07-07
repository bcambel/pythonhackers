from flask import request, jsonify, Blueprint
import logging
from flask.ext.login import login_required, current_user
from pyhackers.helpers import current_user_id
from pyhackers.service.channel import follow_channel
from pyhackers.service.discuss import new_discussion_message, discussion_messages, get_user_discussion_by_nick, new_discussion_follower, remove_discussion_follower
from pyhackers.service.post import new_post, upvote_message
from pyhackers.service.project import project_follow
from pyhackers.service.user import follow_user, get_user_timeline_by_nick, get_user_projects_by_nick


ajax_app = Blueprint('ajax', __name__, url_prefix='/ajax/')

@ajax_app.route('message/<regex(".+"):message_id>/upvote', methods=("POST",))
@login_required
def upvote_message_ctrl(message_id):
    upvote_message(message_id, current_user_id())
    return jsonify({'ok': 1})


@ajax_app.route("message/new", methods=("POST",))
@login_required
def new_message():
    logging.warn(request.form)
    message = request.form.get('message')
    code = request.form.get("code")

    new_post(message, code, current_user_id(), nick=current_user.nick)
    return jsonify({'ok': 1})


@ajax_app.route("followchannel", methods=("POST",))
@login_required
def follow_channel_ctrl():
    user_id = request.form.get("id")
    slug = request.form.get("slug")

    result = follow_channel(user_id, current_user)

    return jsonify({'ok': result})


@ajax_app.route("followuser", methods=("POST",))
@login_required
def follow_user_ctrl():
    user_id = request.form.get("id")
    nick = request.form.get("slug")

    result = follow_user(user_id, current_user)

    return jsonify({'ok': result})


@ajax_app.route("follow", methods=("POST",))
@login_required
def follow():
    project_id = request.form.get("id")
    slug = request.form.get("slug")

    logging.warn(u"Liked %s %s [%s-%s]", project_id, slug, current_user.id, current_user.nick)

    project_follow(project_id, current_user)

    return jsonify({'ok': 1})


@ajax_app.route('discuss/message/new', methods=('POST',))
@login_required
def new_discussion_message_ctrl():
    text = request.form.get("text")
    id = request.form.get("id")

    discussion_id = id
    message_id = new_discussion_message(discussion_id, text, current_user_id(), nick=current_user.nick,topic=topic)

    return jsonify({'id': message_id})


@ajax_app.route('discuss/<regex(".+"):discussion_id>/follow', methods=('POST',))
@login_required
def follow_discussion(discussion_id):
    status = request.form.get("status", "follow")
    logging.warn("Discussion User[{}] => {}".format(current_user_id(), status))
    if status == "follow":
        new_discussion_follower(discussion_id, current_user_id(), nick=current_user.nick)
    else:
        remove_discussion_follower(discussion_id, current_user_id())

    return jsonify({'ok': True})

@ajax_app.route('discuss/<regex(".+"):discussion_id>/messages', methods=('GET',))
def discussion_messages_ctrl(discussion_id):
    after_id = request.args.get("after_id", -1)
    try:
        after_id = int(after_id)
    except:
        after_id = -1

    _ = discussion_messages(discussion_id, after_message_id=after_id, current_user_id=current_user_id())

    discussion, disc_posts, users, counters = _
    discussion_dict = discussion.to_dict()
    discussion_dict.update(**counters.to_dict())

    return jsonify({'discussion': discussion_dict , 'posts': [p.to_dict() for p in disc_posts]}) #, 'users' : users})


@ajax_app.route('user/<regex(".+"):nick>/projects')
def user_projects(nick):
    _ = get_user_projects_by_nick(nick)
    if _ is None:
        return jsonify({'user': None, 'projects': None})

    user, projects = _
    start = 0

    return jsonify({'user': user.to_dict(), 'projects': [f.to_dict(index=start + i + 1) for i, f in enumerate(projects)]})


@ajax_app.route('user/<regex(".+"):nick>/timeline')
def user_timeline(nick):
    after_id = request.args.get("after_id", -1)
    _ = get_user_timeline_by_nick(nick)
    if _ is None:
        return jsonify({'user': None})

    user, timeline = _

    return jsonify({'user': user.to_dict(), 'timeline': [t.to_dict() for t in timeline]})


@ajax_app.route('user/<regex(".+"):nick>/discussions')
def user_discussion(nick):
    after_id = request.args.get("after_id", -1)

    _ = get_user_discussion_by_nick(nick)
    if _ is None:
        return jsonify({'user': None})

    user, discussions = _

    return jsonify({'user': user.to_dict(), 'discussions': [t.to_dict() for t in discussions]})
