from rq import Queue, Connection

__author__ = 'bahadircambel'


with Connection():
    worker_queue = Queue()
