import logging
from flask import request, jsonify, Blueprint
from flask.ext.login import login_required, current_user
from pyhackers.cache import cache
from pyhackers.helpers import render_template, render_base_template, current_user_id
from pyhackers.service.discuss import new_discussion
discuss_app = Blueprint('discuss', __name__, template_folder='templates', url_prefix='/discuss/')


@discuss_app.route('home')
def index():
    return render_base_template('discuss.html')


@discuss_app.route('top')
def top():
    return render_template('discuss.html')


@discuss_app.route('new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title", '')
        text = request.form.get("text", '')
        logging.warn(request.form)
        logging.warn(u"Text:{} -  Title: {}".format(text,title))
        #raise ValueError("Test")

        new_discussion(title, text, current_user_id())

    return jsonify({'ok': 1})
