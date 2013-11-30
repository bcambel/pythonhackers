import os
import sys
from werkzeug.routing import BaseConverter

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.dirname(current_dir)

sys.path.insert(0, source_dir)

from flask import Flask, request, abort, render_template, redirect, jsonify, session

from flaskext.kvsession import KVSessionExtension
import logging
from config import config

from setup import setup_application_extensions

current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = config.get("app", "static")
templates_folder = config.get("app", "templates")
db_conf = config.get("app", "db")

app = Flask(__name__, template_folder='templates')
app.secret_key = config.get("app", "flask_secret")
app.debug = bool(config.get("app", "debug"))
app.config['SQLALCHEMY_DATABASE_URI'] = db_conf


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


def start_app():
    from sentry import init as init_sentry
    # init_sentry(app)
    login_manager = setup_application_extensions(app, '/authenticate')

    from flask.ext.sqlalchemy import SQLAlchemy

    from pyhackers.db import set_db, get_db

    set_db(SQLAlchemy(app))
    DB = get_db()
    @login_manager.user_loader
    def load_user(userid):
        from pyhackers.model.user import User

        logging.warn("[USER]Finding user {}".format(userid))
        try:
            return User.query.get(userid)
        except:
            return None

    from pyhackers.admin import init as admin_init
    from pyhackers.cache import init as cache_init

    cache_init(app)
    admin_init(app,DB)

    from pyhackers.controllers.main import main_app
    #from controllers.oauth.twitter import twitter_bp
    from pyhackers.controllers.oauth.ghub import github_bp

    # app.register_blueprint(twitter_bp)
    app.register_blueprint(github_bp)
    app.register_blueprint(main_app)


if __name__ == "__main__":
    # db.create_all()
    start_app()
    app.run(use_debugger=True, port=5001)