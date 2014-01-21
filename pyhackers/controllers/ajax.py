from flask import request, jsonify, Blueprint, logging
from flask.ext.login import login_required, current_user
from pyhackers.helpers import current_user_id
from pyhackers.service.channel import follow_channel
from pyhackers.service.discuss import new_discussion_message, discussion_messages
from pyhackers.service.project import project_follow
from pyhackers.service.user import follow_user


ajax_app = Blueprint('ajax', __name__, url_prefix='/ajax/')

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
    message_id = new_discussion_message(discussion_id, text, current_user_id())

    return jsonify({'id': message_id})

@ajax_app.route('discuss/<regex(".+"):discussion_id>/messages', methods=('GET',))
def discussion_messages_ctrl(discussion_id):
    after_id = request.args.get("after_id", -1)
    try:
        after_id = int(after_id)
    except:
        after_id = -1
    _ = discussion_messages(discussion_id, after_message_id=after_id)
    discussion, disc_posts, users, counters = _
    discussion_dict = discussion.to_dict()
    discussion_dict.update(**counters.to_dict())

    return jsonify({'discussion': discussion_dict , 'posts': [p.to_dict() for p in disc_posts]}) #, 'users' : users})