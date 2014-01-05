import logging
import time


class MessageWorker():

    def __init__(self, user, message, context):
        self.user = user
        self.message = message
        self.context = context

    def process(self):
        logging.warn("Process {}".format(self.message))

    def index(self):
        logging.warn("Index...{}".format(self.message))

    def url_rewrite(self):
        logging.warn("URL Rewrite..{}".format(self.message))

    def wait(self):
        logging.warn("Long running thing..")
        logging.warn("="*40)
        time.sleep(10)

    def run(self):
        self.process()
        self.index()
        self.url_rewrite()
        self.wait()


def foo(user, message, context):
    logging.warn("[WORKER][FOO] {} - {} - {}".format(user,message,context))
    MessageWorker(user, message, context).run()