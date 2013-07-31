import logging
from flask.ext.wtf import (Form, TextField, PasswordField,
                           SubmitField, Required, ValidationError)
from flask import Flask, request, abort, render_template, redirect, jsonify, session, url_for
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from pyhackers.setup import login_manager
from pyhackers.app import app
from pyhackers.models import init_store, User
from json import loads,dumps
import time
import requests

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


@app.route("/", methods=("GET",))
@app.route("/index", methods=("GET",))
def index():
    links = [
        {'url': 'http://google.com', 'title': 'Google Homepage is updated', 'ago': rand_int(),
         'comment': rand_int(100), 'popularity': rand_int(1004)},
        {'url': 'http://yahoo.com', 'title': 'Yahoo is rising high to the sky with Marissa Meyer', 'ago': rand_int(),
         'comment': rand_int(100), 'popularity': rand_int(1000)},
    ]
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


