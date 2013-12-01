import logging
import requests
from time import time
from pyhackers.config import config, APPS_TO_RUN


class IdGenerator():
    max_time = int(time() * 1000)
    sequence = 0
    worker_id = 1
    epoch = 1356998400000  # 2013-01-01

    def create(self, worker_id=None):
        curr_time = int(time() * 1000)

        if curr_time > IdGenerator.max_time:
            IdGenerator.sequence = 0
            IdGenerator.max_time = curr_time

        IdGenerator.sequence += 1

        if IdGenerator.sequence > 4095:
            # Sequence overflow, bail out
            StatsHandler.errors += 1
            raise ValueError('Clock went backwards! %d < %d' % (curr_time, IdGenerator.max_time))

        IdGenerator.sequence += 1

        if IdGenerator.sequence > 4095:
            StatsHandler.errors += 1
            raise ValueError('Sequence Overflow: %d' % IdGenerator.sequence)

        generated_id = ((curr_time - IdGenerator.epoch) << 23) | ((worker_id or IdGenerator.worker_id) << 10) | IdGenerator.sequence
        StatsHandler.generated_ids += 1
        logging.debug("Created new ID: %s" % generated_id)
        return generated_id


class StatsHandler:
    errors = 0
    generated_ids = 0
    flush_time = time()

    def get(self, flush=False):
        if flush:
            self.flush()

        return {
            'timestamp': time(),
            'generated_ids': StatsHandler.generated_ids,
            'errors': StatsHandler.errors,
            'max_time_ms': IdGenerator.max_time,
            'worker_id': IdGenerator.worker_id,
            'time_since_flush': time() - StatsHandler.flush_time,
        }

    def flush(self):
        StatsHandler.generated_ids = 0
        StatsHandler.errors = 0
        StatsHandler.flush_time = time()


class IDGenClient():
    service_loc = None

    def __init__(self):
        logging.warn("Starting " + self.__class__.__name__)
        self.session = requests.Session()

    def get(self):
        r = self.session.get(self.service_loc)
        return long(r.text.replace("\r\n", ""))


class LocalIDGenClient():
    def __init__(self):
        logging.warn("Starting " + self.__class__.__name__)
        self.idgen = IdGenerator()

    def get(self):
        return self.idgen.create()


idgen_client = None

try:
    IdGenerator.worker_id = int(config.get("idgen", 'worker_id'))
    IDGenClient.service_loc = config.get("app", "idgen_service")

    # if we initialize the IDGen service in this process, lets connect to the internal item..,
    if "idgen" in APPS_TO_RUN:
        idgen_client = LocalIDGenClient()
    else:
        idgen_client = IDGenClient()

except Exception, ex:
    logging.exception(ex)
    pass