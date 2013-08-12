import logging
import random
from json import loads, dumps
import time
import requests
from flask.ext.wtf import (Form, TextField, PasswordField,
                           SubmitField, Required, ValidationError)
from flask import Flask, request, abort, render_template, redirect, jsonify, session, url_for
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from pyhackers.setup import login_manager
from pyhackers.app import app, cache
from pyhackers.models import init_store, User

from pyhackers.model.user import User, new_user
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.config import config

purge_key = config.get("app", 'purge_key')
userStorage = init_store("pyhackers")


def render_base_template(*args, **kwargs):
    try:
        is_logged = int(request.args.get("logged", "1"))
    except Exception as ex:
        logging.exception(ex)
        is_logged = False

    user_data = dumps({'logged': bool(is_logged)})

    kwargs.update(**{'__v__': int(time.time()), 'user_data': user_data})
    return render_template(*args, **kwargs)


@app.errorhandler(400)
def unauthorized(e):
    return render_template('400.html'), 400


@login_manager.user_loader
def load_user(userid):
    logging.warn("Finding user %s" % userid)
    return userStorage.get(userid)


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


@app.route("/", methods=("GET",))
@app.route("/home", methods=("GET",))
@app.route("/index", methods=("GET",))
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
@app.route('/os/<regex(".+"):project>')
def os(project):
    print "looking for", project
    project = OpenSourceProject.query.filter_by(slug=project).first()
    related_projects = OpenSourceProject.query.filter_by(parent=project.slug).order_by(
        OpenSourceProject.watchers.desc())

    return render_base_template("os.html", project=project, related_projects=related_projects)


@cache.cached(timeout=10000)
@app.route('/os')
@app.route('/os/')
def os_list():
    projects = OpenSourceProject.query.limit(2000)

    return render_base_template("os_list.html", projects=projects)


def current_user_logged_in():
    if hasattr(current_user, "id"):
        logging.debug("This is our GUY!!!!! %s" % current_user.id)
        logging.debug("Current User Type: %s, %r" % (type(current_user), current_user.__dict__))
        return True
    else:
        return False


@app.route("/logout")
def logout():
    if current_user_logged_in():
        userStorage.remove(current_user.id)

    logout_user()
    return render_base_template("logout.html", master="login_master.html")


