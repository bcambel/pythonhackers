import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, render_template, redirect, jsonify, session

from flaskext.kvsession import KVSessionExtension
import logging
from config import config, SENTRY_DSN
from raven.contrib.flask import Sentry

from setup import setup_application_extensions

current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = config.get("app", "static")
templates_folder = config.get("app", "templates")
db_conf = config.get("app", "db")

app = Flask(__name__, template_folder='templates')
app.secret_key = config.get("app", "flask_secret")
app.debug = bool(config.get("app", "debug"))
app.config['SQLALCHEMY_DATABASE_URI'] = db_conf

db = SQLAlchemy(app)

from raven.base import DummyClient

if SENTRY_DSN is None:
    sentry = DummyClient()
else:
    try:
        sentry = Sentry(app, dsn=SENTRY_DSN)
        sentry.captureMessage("Configuration is loaded. App is restarted...")
    except Exception, ex:
        logging.exception(ex)
        try:
            error_client = DummyClient(SENTRY_DSN)
        except:
            logging.error("""
======Failed to initialize Sentry client... The sentry client will run in DummyMode
======Restart Application to try to connect to Sentry again
======Check the previous error that output
======CONFIG: SENTRY_DSN => [%s]
======The application will run now...
""" % SENTRY_DSN)


setup_application_extensions(app, '/authenticate')

if __name__ == "__main__":
    from controllers import *

    app.run(use_debugger=True, port=5000)