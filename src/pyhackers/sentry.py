from config import SENTRY_DSN
from raven.contrib.flask import Sentry
from raven.base import DummyClient
import logging

def init(app):
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
