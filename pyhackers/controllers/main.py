# coding=utf-8
from datetime import datetime as dt
import logging
import random
from json import dumps
import time
import calendar
from pyhackers.model.tutorial import Tutorial
import requests
from pyhackers.model.package import Package
from pyhackers.service.post import new_post
from pyhackers.service.channel import follow_channel, load_channel, get_channel_list
from pyhackers.service.project import project_follow, load_project
from pyhackers.service.user import get_profile, get_profile_by_nick, follow_user, load_user
from flask.ext.wtf import Form, TextField, PasswordField, Required
from flask import request, render_template as template_render, Blueprint, redirect, jsonify, abort
from flask.ext.login import current_user, logout_user, login_required
from datetime import datetime as dt
from pyhackers.setup import login_manager
from pyhackers.cache import cache
from pyhackers.model.user import User
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.config import config
from pyhackers.sentry import sentry_client
from sqlalchemy import and_

purge_key = config.get("app", 'purge_key')
debug = config.get("app", "debug")
PRODUCTION = not (debug in ['True', '1', True, 1])
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
                     'user_json': user_data,
                     'channels': get_channel_list(),
                     'PROD': PRODUCTION,
                     'logged_in': bool(is_logged),
                     'year': dt.utcnow().year,
                     })

    return render_template(*args, **kwargs)



cache_buster = calendar.timegm(time.gmtime())


def render_template(*args, **kwargs):
    kwargs.update(**{'cache_buster': cache_buster})
    return template_render(*args, **kwargs)


@main_app.errorhandler(400)
def unauthorized(e):
    return render_template('400.html'), 400


@login_manager.user_loader
def login_load_user(userid):
    logging.warn("Finding user %s" % userid)
    user = User.query.get(userid)

    return user


class LoginForm(Form):
    username = TextField("username", [Required()])
    password = PasswordField("password", [Required()])


def rand_int(maximum=60):
    return int(random.random() * 100) % maximum


def request_force_non_cache():
    if not PRODUCTION:
        return False
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


@main_app.route("/welcome", methods=("GET",))
def welcome():
    return render_base_template("welcome.html")


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
              'btn_top': 'disabled' if list_type == 'top' else '', }

    return render_base_template("index.html", **kwargs)


@main_app.route('/open-source/categories/web-framework')
def project_categories():
    projects = OpenSourceProject.query.filter(OpenSourceProject.categories.contains(["Web Framework"])) \
        .order_by(OpenSourceProject.watchers.desc()).limit(400)

    return render_base_template("os_list.html", projects=projects)


@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/os/<regex(".+"):nick>/<regex(".+"):project>')
@main_app.route('/open-source/<regex(".+"):nick>/<regex(".+"):project>')
def os(nick, project):
    project = project[:-1] if project[-1] == "/" else project
    logging.info(u"looking for %s", project)
    slug = u"%s/%s" % (nick, project)
    project_data = load_project(slug, current_user)

    if project_data is None:
        return "Not found", 404

    project, related_projects, followers = project_data

    return render_base_template("os.html",
                                project=project,
                                related_projects=related_projects,
                                followers=followers, )


@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/os')
@main_app.route('/os/')
@main_app.route('/open-source/')
def os_list():
    projects = OpenSourceProject.query.filter(
        and_(OpenSourceProject.lang == 0, OpenSourceProject.hide is not True)).order_by(
        OpenSourceProject.watchers.desc()).limit(400)

    return render_base_template("os_list.html", projects=projects)


from docutils.core import publish_parts


@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/python-packages/<regex(".+"):package>')
def package_details(package):
    package_obj = Package.query.get(package)
    if package_obj is None:
        return abort(404)

    try:
        description = publish_parts(package_obj.description, writer_name='html')['html_body']
    except:
        description = package_obj.description
        #description = markdown( package.description, autolink=True)

    return render_base_template("package.html", package=package_obj, description=description)


@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/python-packages/')
def package_list():
    packages = Package.query.order_by(Package.mdown.desc()).limit(1000)

    return render_base_template("packages.html", packages=packages)


@main_app.route("/user")
def user():
    user = current_user
    return render_base_template("user.html", user=user)


@main_app.route("/new", methods=['GET', 'POST'])
def new_message():
    if request.method == "POST":
        logging.warn(request.form)
        message = request.form.get('message')
        code = request.form.get("code")

        new_post(message, code, current_user)
        return jsonify({'ok': 1})

    return render_base_template("new_message.html")


def current_user_logged_in():
    if hasattr(current_user, "id"):
        return True
    else:
        return False


@main_app.route("/about")
def about():
    return render_base_template("about.html")


@main_app.route("/coding")
def coding():
    return render_base_template("coding.html")


@main_app.route("/logout")
def logout():
    logout_user()
    return render_base_template("logout.html")


@main_app.route("/profile")
@login_required
def profile():
    #get_profile(current_user)

    user_data = load_user(current_user.id, current_user)
    if user_data is not None:
        user, followers, following, os_projects = user_data
        #print user
        return render_base_template("profile.html", profile=user, followers=followers,
                                    following=following,
                                    os_projects=os_projects)

    return abort(404)


@main_app.route('/channels/<regex(".+"):name>')
def channel(name):
    channel_name = name
    load_channel(name)
    if name == 'lobby':
        channel_name = "Lobby"
    return render_base_template("channel.html", channel_name=channel_name)

#from itertools import repeat

@cache.cached(timeout=10000, unless=request_force_non_cache)
@main_app.route('/user/<regex(".+"):nick>')
def user_profile(nick):
    _ = get_profile_by_nick(nick)
    if _ is not None:
        user, followers, following, os_projects = _
    else:
        return abort(404)

    return render_base_template("user_profile.html",
                                profile=user, followers=followers,
                                following=following,
                                os_projects=os_projects)


@cache.cached(timeout=10000, unless=request_force_non_cache)
def find_tutorial(slug):
    return Tutorial.query.filter_by(slug=slug).first()


@main_app.route('/tutorial/<regex(".+"):nick>/<regex(".+"):tutorial>')
def tutorial(nick, tutorial):
    return render_template("tutorial.html", tutorial=find_tutorial("{}/{}".format(nick, tutorial)))


@main_app.route("/authenticate")
def authenticate():
    return render_base_template('authenticate.html')


@main_app.route("/ajax/followchannel", methods=("POST",))
@login_required
def followchannel():
    user_id = request.form.get("id")
    nick = request.form.get("slug")

    result = follow_channel(user_id, current_user)

    return jsonify({'ok': result})


@main_app.route("/ajax/followuser", methods=("POST",))
@login_required
def followuser():
    user_id = request.form.get("id")
    nick = request.form.get("slug")

    result = follow_user(user_id, current_user)

    return jsonify({'ok': result})


@main_app.route("/ajax/follow", methods=("POST",))
@login_required
def follow():
    project_id = request.form.get("id")
    slug = request.form.get("slug")

    logging.warn("Liked %s %s [%s-%s]", project_id, slug, current_user.id, current_user.nick)

    project_follow(project_id, current_user)

    return jsonify({'ok': 1})