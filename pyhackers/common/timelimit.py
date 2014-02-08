import logging
import threading
import sys
import traceback


class TimeoutError(Exception): pass


def timelimit(timeout=30, test=False):
    """borrowed from web.py"""
    timeout_in_seconds = 30

    def _1(function):
        def _2(*args, **kw):
            class Dispatch(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                    self.setDaemon(True)
                    self.start()

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()

            if not test:

                c = Dispatch()

                if hasattr(timeout, '__call__'):
                    timeout_in_seconds = timeout()
                else:
                    timeout_in_seconds = timeout

                logging.debug("Timeout is %d" % timeout_in_seconds)
                c.join(timeout_in_seconds)

                if c.isAlive():
                    raise TimeoutError, 'took too long'
                if c.error:
                    tb = ''.join(traceback.format_exception(c.error[0], c.error[1], c.error[2]))
                    logging.debug(tb)
                    raise c.error[0], c.error[1]
                return c.result
            else:
                return function(*args, **kw)

        return _2

    return _1