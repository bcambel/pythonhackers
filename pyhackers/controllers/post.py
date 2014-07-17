import logging
from flask import request, jsonify, Blueprint, redirect, abort, make_response
from flask.ext.login import login_required, current_user
from pyhackers.helpers import render_base_template
from pyhackers.service.post import load_post_by_id, delete_post, load_post_replies


post_app = Blueprint('post', __name__, template_folder='templates', url_prefix='/post/')

@post_app.route('<regex(".+"):id>')
def post(id):
    logging.warn(id)
    post, user = load_post_by_id(id)

    if post.deleted:
        return render_base_template("post_deleted.html", post=post,post_user=user)
    else:
        post_replies = load_post_replies(id, current_user.id)
        return render_base_template("post.html", post=post,post_user=user, replies=post_replies)

@post_app.route('<regex(".+"):id>/replies')
def post_replies(id):
    logging.warn(id)
    post,user = load_post_by_id(id)
    return render_base_template("post.html",post=post,post_user=user)
