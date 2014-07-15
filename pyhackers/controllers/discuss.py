import logging
from flask import request, jsonify, Blueprint, redirect, abort, make_response
from flask.ext.login import login_required, current_user
from pyhackers.cache import cache
from pyhackers.helpers import render_template, render_base_template, current_user_id
from pyhackers.service.discuss import new_discussion, load_discussion, new_discussion_message, load_discussions, load_discussions_by_topic_id
from pyhackers.service.topic import load_topics, topic_slug_to_id

discuss_app = Blueprint('discuss', __name__, template_folder='templates', url_prefix='/discuss/')


@discuss_app.route('home')
def index():
    discussions = load_discussions()
    topics = load_topics()
    return render_base_template('discuss.html', discussions=discussions,topics=topics)


@discuss_app.route('top')
def top():
    return render_template('discuss.html')


@discuss_app.route('<regex(".+"):slug>/<regex(".+"):id>')
@discuss_app.route('<regex(".+"):slug>/<regex(".+"):id>/')
@discuss_app.route('<regex(".+"):id>/')
def discussion_ctrl(id, slug=None):

    discussion_data = load_discussion(id, current_user_id())
    discussion, disc_posts, message, counters, disc_user = discussion_data
    related_discussions = load_discussions()

    return render_base_template("discussion.html", discussion=discussion,
                                message=message,
                                discussion_user=disc_user,
                                posts=[],
                                counters=counters,
                                related_discussions=related_discussions,
                                )

@discuss_app.route('topic/<regex(".+"):slug>')
def discuss_topic_ctrl(slug):
    #response = make_response("ok")
    id = topic_slug_to_id(slug)
    discussions = load_discussions_by_topic_id(id, slug )
    topics = load_topics()
    return render_base_template('discuss.html', discussions=discussions,topics=topics)
    #return response

@discuss_app.route('new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title", '')
        text = request.form.get("text", '')
        topic = request.form.get("topic", None)

        logging.warn(request.form)
        logging.warn(u"Text:{} -  Title: {} Topic {}".format(text, title, topic))
        #raise ValueError("Test")

        discuss_id, slug = new_discussion(title, text, current_user.id, topic=topic)

        return redirect("/discuss/{}/{}".format(slug, discuss_id))
        #return jsonify({'id': str(discuss_id), 'slug': slug})

    return jsonify({'ok': 1})




