import logging
from cqlengine import connection


def setup(hosts=None, keyspace=None):

    model_keyspace = None
    cassa_hosts = None

    if hosts is None or keyspace is None:
        from pyhackers.config import config
        cassa_hosts = hosts or config.get("cassandra", "host")
        model_keyspace = config.get("cassandra", "keyspace")
    else:
        model_keyspace = keyspace
        cassa_hosts = hosts

    if isinstance(cassa_hosts, basestring):
        cassa_hosts = cassa_hosts.split(",")

    logging.warn("Keyspace: [{}] Hosts: [{}]".format(model_keyspace, cassa_hosts))

    return cassa_hosts, model_keyspace


def connect(cassa_host_list, default_keyspace):
    if cassa_host_list is None:
        pass
        #hosts = ['127.0.0.1:9160']

    connection.setup(cassa_host_list, default_keyspace=default_keyspace)