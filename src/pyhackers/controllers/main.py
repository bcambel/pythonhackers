import logging
from flask.ext.wtf import (Form, TextField, PasswordField,
                           SubmitField, Required, ValidationError)
from flask import Flask, request, abort, render_template, redirect, jsonify, session, url_for
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from pyhackers.setup import login_manager
from pyhackers.app import app, cache
from pyhackers.models import init_store, User
from json import loads, dumps
import time
import requests
from pyhackers.model.user import User, new_user

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


import random


def rand_int(maximum=60):
    return int(random.random() * 100) % maximum


def request_force_non_cache():
    return request.args.get("purge", False) in ["True", "1", "ok", True]


@cache.memoize(timeout=20, unless=request_force_non_cache)
def get_reddit_top_python_articles(list_type='top'):

    keys = ['top', 'new', 'hot']

    url = "http://www.reddit.com/r/python/%s.json" % list_type
    logging.warn("Fetch REDDIT %s" % url )

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
        new_user(post['user'],"%s@gmail.com" % post['user'])
        reddit_python_posts.append(post)

    return reddit_python_posts


@app.route("/", methods=("GET",))
@app.route("/index", methods=("GET",))
def index():
    list_type = request.args.get("list", 'top')
    links = get_reddit_top_python_articles(list_type=list_type)
    return render_base_template("index.html", links=sorted(links, key=lambda x: x.get("popularity"), reverse=True))


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


