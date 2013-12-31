import logging
from tweepy.streaming import StreamListener, json
from tweepy import OAuthHandler, API
from tweepy import Stream
from dateutil import parser as dtparser
from pyhackers.config import config
import redis
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """

    def __init__(self):
        #kafka = KafkaClient("localhost", 9092)
        #self.producer = SimpleProducer(kafka, "pyhackers-rt")
        super(StdOutListener, self).__init__()

    def on_data(self, data):
        obj = json.loads(data)
        #text = obj.get("text") or ""

        if "limit" in obj:
            logging.warn(obj)
            return True

        if "user" not in obj:
            logging.warn(obj)
            return True

        tweet_id = str(obj.get("id_str"))
        self.publish_to_redis(data, tweet_id)
        return True

    @staticmethod
    def publish_to_redis(data, _):
        redis_conn.publish("realtime", data)
        #self.producer.send_messages(data)

    @staticmethod
    def write_to_disk(data, tweet_id):
        with open('.tweets/{}.json'.format(tweet_id), "w") as f:
            f.write(data)

    def on_error(self, status):
        print status


redis_conn = None


def start():
    global redis_conn
    redis_conn = redis.StrictRedis(host="localhost", port=6379, db=0)
    consumer_key = config.get("twitter", "client_id")
    consumer_secret = config.get("twitter", "client_secret")
    access_token = config.get("twitter", "access_token")
    access_token_secret = config.get("twitter", "access_token_secret")

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    friend_ids = api.friends_ids()
    stream = Stream(auth, l)
    #        ,track=['startup','entrepreneurship','marketing','SEO']
    stream.filter(follow=friend_ids, track=['clojure']) #,track=[
    #'entrepreneurship','StartUp','SaaS','github','ycombinator','techstars',
    #'cassandra','mysql','mongodb','quora',
    #'scala','erlang','golang','python','entrepreneur','marketing'])