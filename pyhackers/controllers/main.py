import logging
import random
from json import dumps
import time
from datetime import datetime as dt
from pyhackers.model.action import Action, ActionType
import requests
from flask.ext.wtf import Form, TextField, PasswordField, Required
from flask import request, render_template, Blueprint,redirect, jsonify
from flask.ext.login import current_user, logout_user, login_required
from pyhackers.setup import login_manager

from pyhackers.cache import cache
from pyhackers.model.user import User
from pyhackers.model.message import Message
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.config import config
from pyhackers.db import DB as db

purge_key = config.get("app", 'purge_key')

main_app = Blueprint('main', __name__, template_folder='templates')


def render_base_template(*args, **kwargs):
    try:
        logging.warn(current_user.is_anonymous())
        is_logged = not current_user.is_anonymous()  #int(request.args.get("logged", "1"))
    except Exception as ex:
        logging.exception(ex)
        is_logged = False

    active_user = current_user.jsonable() if not current_user.is_anonymous() else {}
    user_data = dumps(active_user)
    logging.warn(user_data)
    kwargs.update(**{'__v__': int(time.time()),
                     'user': active_user,
                     'user_json' : user_data,
                     'PROD' : True,
                     'logged_in': bool(is_logged)})

    return render_template(*args, **kwargs)


@main_app.errorhandler(400)
def unauthorized(e):
    return render_template('400.html'), 400


@login_manager.user_loader
def load_user(userid):

    logging.warn("Finding user %s" % userid)
    user = User.query.get(userid)

    return user


class LoginForm(Form):
    username = TextField("username", [Required()])
    password = PasswordField("password", [Required()])


def rand_int(maximum=60):
    return int(random.random() * 100) % maximum


def request_force_non_cache():
    return request.args.get(purge_key, False) in ["True", "1", "ok", True]


@cache.memoize(timeout=10000, unless=request_force_non_cache)
def get_reddit_top_python_articles(list_type='top'):
    keys = ['top', 'new', 'hot']

    url = "http://www.reddit.com/r/python/%s.json" % list_type
    logging.warn("Fetch REDDIT %s" % url)

    assert list_type in keys

    r = requests.get(url)

    reddit_posts = r.json()
    reddit_python_posts = []

    for red in reddit_posts['data']['children']:
        post = {}
        data = red['data']
        post['url'] = data['url']
        post['popularity'] = data['score']
        post['comment'] = data.get('num_comments', 0)
        post['title'] = data.get('title', '')
        post['domain'] = data.get('domain', '')
        post['ago'] = int((int(time.time()) - data.get('created_utc')) / 3600)
        post['user'] = data.get("author")

        reddit_python_posts.append(post)

    return reddit_python_posts


@main_app.route("/", methods=("GET",))
def main():
    if current_user.is_anonymous():
        return render_base_template("welcome.html")
    else:
        return redirect('/home')

@main_app.route("/home", methods=("GET",))
@main_app.route("/index", methods=("GET",))
@main_app.route("/links", methods=("GET",))
def index():
    list_type = request.args.get("list", 'top')

    links = get_reddit_top_python_articles(list_type=list_type)
    kwargs = {'links': sorted(links, key=lambda x: x.get("popularity"), reverse=True),
              'btn_hot': 'disabled' if list_type == 'hot' else '',
              'btn_new': 'disabled' if list_type == 'new' else '',
              'btn_top': 'disabled' if list_type == 'top' else '',
    }

    return render_base_template("index.html", **kwargs)


@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/os/<regex(".+"):user>/<regex(".+"):project>')
def os(user, project):
    print "looking for", project
    project = project[:-1] if project[-1] == "/" else project
    print "looking for", project
    slug = "%s/%s" % (user, project)
    project = OpenSourceProject.query.filter_by(slug=slug).first()
    if project is None:
        return "Not found", 404

    related_projects = OpenSourceProject.query.filter_by(parent=slug).order_by(
        OpenSourceProject.watchers.desc()).limit(100)

    return render_base_template("os.html", project=project, related_projects=related_projects)


@cache.cached(timeout=10000)
@main_app.route('/os')
@main_app.route('/os/')
def os_list():
    projects = OpenSourceProject.query.order_by(OpenSourceProject.watchers.desc()).limit(400)

    return render_base_template("os_list.html", projects=projects)


@main_app.route("/user")
def user():
    user = current_user
    return render_base_template("user.html", user=user)

@main_app.route("/new", methods=['GET', 'POST'])
def new_message():
    if request.method == "POST":
        logging.warn(request.form)
        m = Message()
        m.user_id = current_user.id
        m.content = request.form.get('message')
        m.content_html = request.form.get('code')
        db.session.add(m)
        db.session.commit()

    return render_base_template("new_message.html")


def current_user_logged_in():
    if hasattr(current_user, "id"):
        return True
    else:
        return False


@main_app.route("/coding")
def coding():
    return render_base_template("coding.html")

@main_app.route("/logout")
def logout():
    if current_user_logged_in():
        pass

    logout_user()
    return render_base_template("logout.html", master="login_master.html")


@main_app.route("/profile")
def profile():

    return render_base_template("profile.html")


@main_app.route("/ajax/follow", methods=("POST",))
@login_required
def follow():
    project_id = request.form.get("id")
    slug = request.form.get("slug")

    logging.warn("Liked %s %s [%s-%s]", project_id, slug, current_user.id, current_user.nick)

    a = Action()
    a.from_id = current_user.id
    a.to_id = project_id
    a.action = ActionType.FollowProject
    a.created_at = dt.utcnow()
    db.session.add(a)
    db.session.commit()



    return jsonify({'ok':1})