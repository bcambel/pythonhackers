import sys
import os
from rq import Queue, Worker, Connection
from rq.contrib.sentry import register_sentry
from rq.logutils import setup_loghandlers

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.dirname(current_dir)

sys.path.insert(0, source_dir)

if __name__ == '__main__':
    # Tell rq what Redis connection to use
    from pyhackers.app import start_app
    start_app(soft=True)
    from pyhackers.sentry import sentry_client

    setup_loghandlers("DEBUG")

    with Connection():
        q = Queue()
        w = Worker(q)

        register_sentry(sentry_client, w)
        w.work()