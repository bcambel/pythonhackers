import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.dirname(current_dir)

sys.path.append(source_dir)

from app import app, start_app

start_app()

import newrelic.agent

newrelic.agent.initialize(os.path.join(current_dir, 'newrelic.ini'), 'staging')

application = newrelic.agent.wsgi_application()(app)
