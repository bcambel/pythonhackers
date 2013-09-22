import logging
import random
from json import dumps
import time
import requests
from flask.ext.wtf import Form, TextField, PasswordField, Required
from flask import request, render_template, Blueprint
from flask.ext.login import current_user, logout_user
from setup import login_manager

from cache import cache
from model.user import User
from model.os_project import OpenSourceProject
from config import config

purge_key = config.get("app", 'purge_key')

main_app = Blueprint('main', __name__, template_folder='templates')


def render_base_template(*args, **kwargs):
    try:
        is_logged = int(request.args.get("logged", "1"))
    except Exception as ex:
        logging.exception(ex)
        is_logged = False

    user_data = dumps({'logged': bool(is_logged),
                       'user': current_user.jsonable()})

    kwargs.update(**{'__v__': int(time.time()), 'user_data': user_data})
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
    projects = OpenSourceProject.query.limit(400)

    return render_base_template("os_list.html", projects=projects)


@main_app.route("/user")
def user():
    user = current_user
    return render_base_template("user.html", user=user)


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


