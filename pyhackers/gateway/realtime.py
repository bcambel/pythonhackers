from Queue import Queue
import argparse
import logging
import textwrap
import threading
import time
#from pyhackers.utils import files_in
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from twisted.internet import reactor, task
from autobahn.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS
import simplejson as json
import redis
from os import listdir
from os.path import join, isfile


def files_in(directory):
    for f in listdir(directory):
        if isfile(join(directory, f)):
            yield join(directory, f)
    return


redis_conn = None

logging.basicConfig(format='[%(asctime)s](%(filename)s#%(lineno)d)%(levelname)-7s %(message)s',
                    level=logging.NOTSET)

queue = Queue()


def publish_to_tenants():
    if not len(EchoServerProtocol.tenants):
        return

    msg = queue.get(timeout=None)
    if msg is None:
        return

    msg = str(msg) if msg is not None else ""
    #logging.warn("Queue: {}".format(msg))

    #logging.warn("Deliver tweets")
    for t in EchoServerProtocol.tenants:
        t.sendMessage(msg, False)



class EchoServerProtocol(WebSocketServerProtocol):
    tenants = []

    def onOpen(self):
        logging.warn(u"connection accepted from peer {}".format(self.peerstr))


    def onMessage(self, payload, binary):
        self.tenants.append(self)
        logging.warn(u"connection accepted from peer %s" % self.peerstr)
        logging.warn(u"Message: {}".format(payload))

    def onClose(self, *args):
        self.tenants.remove(self)
        logging.warn("{} - {} - {}".format(*args))

directory = '/Users/bahadircambel/code/learning/pythonhackers/.tweets/'


class PubSubKafkaListener(threading.Thread):
    def __init__(self,consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def iterate(self):
        for message in self.consumer:
            logging.warn(message)
            queue.put(message)

    def run(self):
        self.iterate()
        logging.warn("Exit loop")



class PubSubRedisListener(threading.Thread):
    def __init__(self,r,channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def work(self, data):
        queue.put(data)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                logging.warn(self, "unsubscribed and finished")
                break
            else:
                self.work(item['data'])

if __name__ == "__main__":
    from twisted.python import log

# Taken from https://twistedmatrix.com/documents/12.0.0/core/howto/logging.html
    log.startLogging(open('console.log', 'w'))
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent(''))

    parser.add_argument('--wsport', type=int, default=10001, help="WebSocket Service Port")
    parser.add_argument('--redis', type=str, default='localhost', help="Redis location")

    args = parser.parse_args()





    def listen_redis():
        redis_conn = redis.StrictRedis(host=args.redis, port=6379, db=0)
        redis_listener = PubSubRedisListener(redis_conn,['realtime'])
        redis_listener.daemon = True
        redis_listener.start()

    def listen_kafka():
        kafka = KafkaClient("localhost", 9092)
        consumer = SimpleConsumer(kafka,"socket","pyhackers-rt")
        kafka_listener = PubSubKafkaListener(kafka, consumer)
        kafka_listener.daemon = True
        kafka_listener.start()


    listen_redis()



    l = task.LoopingCall(publish_to_tenants)
    l.start(0.1)

    factory = WebSocketServerFactory("ws://localhost:{}".format(args.wsport), debug=True)
    factory.protocol = EchoServerProtocol
    listenWS(factory)

    reactor.run()