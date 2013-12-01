import sys
from datetime import datetime as dt
from functools import wraps
import zlib
import msgpack
import pycassa
from pycassa.pool import ConnectionPool
from pycassa.index import create_index_clause, create_index_expression
from pycassa.cassandra.ttypes import NotFoundException, ConsistencyLevel
from pyhackers.common import unix_time_millisecond, time_with_ms, epoch_to_date, unix_time
from pyhackers.config import config

pool = ConnectionPool("sweetio", [config.cassandra])
status_cf = pycassa.ColumnFamily(pool, "status")
user_timeline_cf = pycassa.ColumnFamily(pool, "user_timeline")
user_cf = pycassa.ColumnFamily(pool, "user2")
channel_timeline_cf = pycassa.ColumnFamily(pool, "channel_timeline")

#create column family user_following_timeline with comparator = IntegerType;
user_following_timeline_cf = pycassa.ColumnFamily(pool, "user_following_timeline")
counters_cf = pycassa.ColumnFamily(pool, "counters")

status_upvotes_cf = pycassa.ColumnFamily(pool, "status_upvotes")
status_downvotes_cf = pycassa.ColumnFamily(pool, "status_downvotes")
status_replies_cf = pycassa.ColumnFamily(pool, "status_replies")
status_resweets_cf = pycassa.ColumnFamily(pool, "status_resweets")
status_favs_cf = pycassa.ColumnFamily(pool, "status_favs")

user_follower_cf = pycassa.ColumnFamily(pool, "user_followers")
user_following_cf = pycassa.ColumnFamily(pool, "user_following")

user_upvotes_cf = pycassa.ColumnFamily(pool, "user_upvotes")
user_downvotes_cf = pycassa.ColumnFamily(pool, "user_downvotes")
user_replies_cf = pycassa.ColumnFamily(pool, "user_replies")
user_favs_cf = pycassa.ColumnFamily(pool, "user_favs")
user_resweets_cf = pycassa.ColumnFamily(pool, "user_resweets")

# user_upvotes
# status_upvotes
# status_retweets { "status_id" : { <status_id> : <user_id> } }
# status_replies
# status_favorites
# status_flags
# conversation =>

not_found_dict = {"error": "Not found"}


class Gateway():
    pass


def notify(message):
    print "New message is here! {}".format(message)


class reporter():
    def captureException(self):
        pass


error_reporter = reporter()


def write(msg):
    sys.stdout.write("[%s] CACHE::%s\n" % (time_with_ms(dt.utcnow()), msg))


class CassandraGateway(Gateway):
    def channel_timeline(self, channel_id_or_name, after_id=""):
        try:
            reverse = not isinstance(after_id, long)

            ch_timeline_items = channel_timeline_cf.get(channel_id_or_name,
                                                        column_reversed=reverse, column_count=20, column_start=after_id)
        except (NotFoundException, Exception):
            return []

        return self.get_statuses(ch_timeline_items, exclude=after_id)

    def timeline(self, user_id, after_id=""):
        try:
            reverse = not isinstance(after_id, long)
            timeline_status_ids = user_following_timeline_cf.get(user_id, column_reversed=reverse, column_count=20,
                                                                 column_start=after_id)
        except NotFoundException:
            return []

        return self.get_statuses(timeline_status_ids, exclude=after_id)

    def user_timeline(self, user_id, after_id=''):
        try:
            reverse = not isinstance(after_id, long)
            timeline_items = user_timeline_cf.get(str(user_id), column_count=20, column_reversed=reverse,
                                                  column_start=after_id)
        except (NotFoundException, Exception):
            return []

        return self.get_statuses(timeline_items, exclude=after_id)

    def get_single_status(self, status_id):
        status = status_cf.get(status_id)
        # write(status)
        data = status.get("data");
        status_post = msgpack.unpackb(zlib.decompress(data))
        status_post["user"] = self.get_user(status_post.get("user_id"))

        try:
            stats = counters_cf.get(status_id)
            write(stats)
            status_post["stats"] = stats
        except NotFoundException:
            pass

        return status_post

    def get_statuses(self, timeline_items, exclude=None):
        status_ids = []

        for ts, id in timeline_items.iteritems():
            if exclude is not None and str(ts) == str(exclude):
                continue
            status_ids.append(id)

        statuses = status_cf.multiget(status_ids)

        status_messages = {}
        status_messages_sorted = []
        user_ids = []

        for key, post in statuses.iteritems():
            status = msgpack.unpackb(zlib.decompress(post.get("data")))
            user_ids.append(status.get("user_id"))
            status_messages[key] = status

        users = user_cf.multiget(user_ids)
        user_dict = {}

        for user_id, columns in users.iteritems():
            for key, val in columns.iteritems():
                if key == "data":
                    # sys.stdout.write("\n%s %s \nZLIB:%r\n" % (user_id,key,val))
                    user_dict[user_id] = msgpack.unpackb(zlib.decompress(val))
                    user_dict[user_id]["stats"] = self.get_user_stats(user_id)

        for ts, id in timeline_items.iteritems():
            message = status_messages.get(id)

            if message is not None:
                message["id"] = str(message['id'])
                message["user"] = user_dict.get(message.get("user_id"))
                message["published_at"] = epoch_to_date(long(message["published_at"]))

                status_messages_sorted.append(status_messages.get(id))

        return status_messages_sorted

    def new_status(self, status_dict, reply_to_id=None, reply_to_user_id=None):

        notify(status_dict)

        if status_dict is None or not isinstance(status_dict, dict):
            return False

        id = long(str(status_dict.get("id")))
        user_id = str(status_dict.get("user_id"))
        channels = status_dict.get("channels")

        status_cf.insert(str(id), {"user_id": user_id, "data": zlib.compress(msgpack.packb(status_dict))})

        ts_id = {id: str(id)}
        #		write("INT: %d vs %s" % (id , str(id)))

        for channel in channels:
            channel_timeline_cf.insert(str(channel), ts_id)

        followers = [f for f in self.get_followers(user_id)]

        for f in followers:
            user_following_timeline_cf.insert(f, ts_id)

        user_timeline_cf.insert(user_id, ts_id)

        #increase status count of the user
        # why there is a user_<id> structure ?
        # well we could submit all our counters to this column family..
        # status ids are registered directly
        # user ids are user_<id> format
        #
        counters_cf.add("user_" + str(user_id), "statuses")

        if reply_to_id is not None:
            counters_cf.add("%s" % reply_to_id, "replies")

    def incr_status_retweet(self, status_id):
        counters_cf.add("%s" % status_id, "resweets")

    def new_channel(self, channel_dict):
        pass

    def new_user(self, id, nick, user_dict):
        user_cf.insert(str(id), {"nick": nick, "data": zlib.compress(msgpack.packb(user_dict))})

    def get_user(self, user_id):
        try:
            #read_consistency_level=ConsistencyLevel.QUORUM
            user = user_cf.get(str(user_id))

            user_dict = msgpack.unpackb(zlib.decompress(user.get("data")))

            if not user_dict.has_key("id"):
                user_dict["id"] = user_id

            return user_dict

        except NotFoundException:
            return None


    def get_user_by_nick(self, user_nick):
        nick_expression = create_index_expression('nick', user_nick)
        clause = create_index_clause([nick_expression], count=1)
        user_dict = None
        for key, user in user_cf.get_indexed_slices(clause):
            user_dict = msgpack.unpackb(zlib.decompress(user.get("data")))

        return user_dict

    def follow_user(self, following_user_id, follower_user_id):
        epoch = int(unix_time(dt.utcnow()))

        user_follower_cf.insert(str(following_user_id), {str(follower_user_id): str(epoch)})
        user_following_cf.insert(str(follower_user_id), {str(following_user_id): str(epoch)})

        counters_cf.add("user_" + str(following_user_id), "followers")
        counters_cf.add("user_" + str(follower_user_id), "following")

    def unfollow_user(self, following_user_id, follower_user_id):
        user_follower_cf.remove(str(following_user_id), columns=[str(follower_user_id)])
        user_following_cf.remove(str(follower_user_id), [str(following_user_id)])

        counters_cf.add("user_" + str(following_user_id), "followers", value=-1)
        counters_cf.add("user_" + str(follower_user_id), "following", value=-1)

    def get_followers(self, user_id):
        try:
            follower_dict = user_follower_cf.get(str(user_id))
        except NotFoundException:
            return

        for key, val in follower_dict.iteritems():
            yield key

    def get_following(self, user_id):
        try:
            following_dict = user_following_cf.get(str(user_id))
        except NotFoundException:
            return None
        return following_dict

    def get_user_stats(self, user_id):

        try:
            return counters_cf.get("user_%s" % str(user_id))
        except NotFoundException:
            return None

    #TODO: Refactor the following methods

    def status_fav(self, status_id, user_id):
        ms = long_now()
        user_favs_cf.insert(str(user_id), {status_id: ""})
        status_favs_cf.insert(str(status_id), {ms: user_id})
        counters_cf.add(str(status_id), "favs")
        counters_cf.add("user_" + str(user_id), "favs")

    def status_upvote(self, status_id, user_id):
        ms = long_now()
        user_upvotes_cf.insert(str(user_id), {status_id: ""})
        status_upvotes_cf.insert(str(status_id), {ms: user_id})
        counters_cf.add(str(status_id), "upvote")
        counters_cf.add("user_" + str(user_id), "upvote")

    def status_downvote(self, status_id, user_id):
        ms = long_now()
        user_downvotes_cf.insert(str(user_id), {status_id: ""})
        status_downvotes_cf.insert(str(status_id), {ms: user_id})
        counters_cf.add(str(status_id), "downvote")
        counters_cf.add("user_" + str(user_id), "downvote")

    def status_reply(self, status_id, user_id):
        pass

    def status_resweet(self, status_id, user_id, new_status_id):
        user_resweets_cf.insert(str(user_id), {status_id: ""})
        status_resweets_cf.insert(str(status_id), {new_status_id: str(user_id)})
        #counters_cf.add("%s"%status_id,"resweets")
        self.incr_status_retweet(status_id)


def long_now():
    return long(unix_time_millisecond(dt.utcnow()))


gateway = CassandraGateway()


class cassandra_cache:
    @classmethod
    def skip_if_possible(cls, proxy_func):
        @wraps(proxy_func)
        def get_data(*args, **kwargs):
            if kwargs.has_key("use_cache") and not kwargs["use_cache"]:
                return proxy_func(*args, **kwargs)

            success, result = cls.call_cache_function(False, proxy_func.__name__, None, *args, **kwargs)
            if not success:
                return proxy_func(*args, **kwargs)
            else:
                return result

        return get_data


    @classmethod
    def after(cls, name=None, condition=None):
        """
        Handles the parameter passing of the decorator.
        If the condition met, call our target function.
        :param cls:
        :param condition:
        :return:
        """

        def after_call(proxy_func):

            @wraps(proxy_func)
            def get_data(*args, **kwargs):

                write("WRAPPER:BEGIN")
                # write(args)
                # write(kwargs)
                # write(dir(proxy_func))
                # write(proxy_func)
                result = proxy_func(*args, **kwargs)

                try:
                    func_name = name or proxy_func.__name__

                    success, cache_result = cls.call_cache_function(True, func_name, result, *args, **kwargs)
                    return cache_result or result
                #					else:
                #						write("Results did not match %r vs %r\n" % (result,condition))
                except:
                    cache_result = None
                    #					error_reporter.captureException()
                    raise

            return get_data

        return after_call

    @classmethod
    def call_cache_function(cls, expect_actual_result, method, actual_call_result, *args, **kwargs):
    #		if hasattr(cls,proxy_func.__name__):
        success, result = False, None

        try:
            fn = getattr(cls, method)

        except:
            write("[%s]Method not found in Cassandra" % method)
            # delay the message capture by somehow.
            #			error_reporter.captureMessage("Method not found in Cassandra: %s" % method)

            return False, None

        try:
            write("BEGIN::%s" % method)
            if not expect_actual_result:
                success, result = fn(*args, **kwargs)
            else:
                success, result = fn(actual_call_result, *args, **kwargs)
        except Exception, ex:
            error_reporter.captureException()
            write("EXCEPTION[%s]:%s" % (method, ex))
        finally:
            write("END::%s" % method)
            return success, result

    @classmethod
    def follow_user(cls, result, *args, **kwargs):
        following_user_id = args[1];
        follower_user_id = args[2]
        if not isinstance(follower_user_id, basestring):
            follower_user_id = str(follower_user_id.id)

        write("Follow USER: %s %s" % (str(following_user_id), str(follower_user_id)))
        try:
            gateway.follow_user(following_user_id, follower_user_id)
        except:
            raise

        return True, True

    @classmethod
    def unfollow_user(cls, result, *args, **kwargs):
        following_user_id = args[1]
        follower_user_id = args[2]
        if not isinstance(follower_user_id, basestring):
            follower_user_id = str(follower_user_id.id)

        write("UNFOLLOW USER: %s %s" % (str(following_user_id), str(follower_user_id)))
        gateway.unfollow_user(following_user_id, follower_user_id)
        return True, True

    @classmethod
    def get_followers(cls, *args, **kwargs):
        following_user_id = args[1]
        follower_ids = [f for f in gateway.get_followers(following_user_id.get("id"))]
        followers = []
        for id in follower_ids:
            user = gateway.get_user(id)
            if user is not None:
                followers.append(user)
        return True, followers


    @classmethod
    def get_following(cls, *args, **kwargs):
        following_user_id = args[1]
        following = []

        for f in gateway.get_following(following_user_id.get("id")):
            user = gateway.get_user(f)
            if user is not None:
                following.append(user)
        return True, following

    @classmethod
    def timeline_cache(cls, *args, **kwargs):
        write("Timeline Cache")
        return False, None

    @classmethod
    def channel_timeline(cls, *args, **kwargs):
        ch_id = args[1]
        after_id = kwargs.get("after_id", "")
        if after_id is None or ( isinstance(after_id, basestring) and not len(after_id)):
            after_id = ""
        else:
            after_id = long(after_id)

        write("CHANNEL after_id: %s" % after_id)

        ch_tm = gateway.channel_timeline(ch_id, after_id=after_id)

        if isinstance(ch_tm, list):
            write("END::Found %d recs" % len(ch_tm))

        return True, (list(reversed(ch_tm)) if not isinstance(after_id, long) else ch_tm)

    @classmethod
    def timeline(cls, *args, **kwargs):
        # write(args)
        # write(kwargs)

        user_id = None
        user = kwargs.get('user', None)

        if user is None:
            return False, []

        if hasattr(user, "id"):
            user_id = str(user.id)
        elif hasattr(user, "get") and "id" in user:
            user_id = str(user.get("id"))

        if user_id is None:
            return False, []

        after_id = kwargs.get("after_id", "")
        if after_id is None or (isinstance(after_id, basestring) and not len(after_id)):
            after_id = ""
        else:
            after_id = long(after_id)

        write("TIMELINE after_id: %s" % after_id)

        timeline = gateway.timeline(user_id, after_id=after_id)

        return True, (list(reversed(timeline)) if not isinstance(after_id, long) else timeline)

    @classmethod
    def get_after_id(cls, **kwargs):
        after_id = kwargs.get("after_id", "")
        if after_id is None or (isinstance(after_id, basestring) and not len(after_id)):
            after_id = ""
        else:
            after_id = long(after_id)
        return after_id

    @classmethod
    def user_timeline(cls, *args, **kwargs):

        user_id = args[1]
        after_id = cls.get_after_id(**kwargs)

        write("BEGIN::User timeline: %s" % user_id)

        id = str(user_id.id) if hasattr(user_id, "id") else str(user_id)
        user_timeline = gateway.user_timeline(id, after_id=after_id)

        if isinstance(user_timeline, list):
            write("END::Found %d recs" % len(user_timeline))

        return True, (list(reversed(user_timeline)) if not isinstance(after_id, long) else user_timeline)

    @classmethod
    def status_insert(cls, new_post, *args, **kwargs):
        write("BEGIN::Status insert")

        if new_post is None:
            return True, None

        write(args)
        replyToId = kwargs.get("reply_to_id", None)
        replyToUserId = kwargs.get("reply_to_user_id", None)

        gateway.new_status(new_post.json(date_converter=unix_time_millisecond), reply_to_id=replyToId,
                           reply_to_user_id=replyToUserId)
        write("END::Status insert")
        return True, new_post

    @classmethod
    def status_resweet(cls, ret_val, *args, **kwargs):
        id = long(args[1])
        user = args[2]

        user_id = str(user.id) if user is not None and hasattr(user, "id") else None

        # status = gateway.get_single_status(id)
        # write(status)
        new_status_id = ret_val.id
        #increate status ReSweet count
        gateway.status_resweet(id, user_id, new_status_id)


        # add history record to notify userA that somebody resweeted their status post.


        return True, ret_val.json()

    actions = ["fav", "upvote", "email", "flag", "resweet", "email", 'downvote', 'info']

    @classmethod
    def status_action_handler(cls, *args, **kwargs):
        status_id = long(args[1])
        action = args[2]
        try:
            user = args[3]
        except IndexError, ie:
            user = kwargs.get("user", None)

        user_id = str(user.id) if user is not None and hasattr(user, "id") else "None"

        write("Id:%s Action:%s User:%s" % (status_id, action, user_id))

        if action == "upvote":
            gateway.status_upvote(status_id, user_id)
        elif action == "fav":
            write("calling fav action")
            gateway.status_fav(status_id, user_id)
        elif action == "downvote":
            gateway.status_downvote(status_id, user_id)
        elif action == "info":
            return True, gateway.get_single_status(str(status_id))

        return True, True

    @classmethod
    def user_profile(cls, *args, **kwargs):
        user_id = args[1]
        write("USER Lookup (%s)" % user_id)

        user = gateway.get_user_by_nick(user_id)

        followers = [f for f in gateway.get_followers(user.get("id"))]

        if user is None:
            return False, not_found_dict

        user["followers"] = followers
        user["stats"] = gateway.get_user_stats(user.get("id"))

        return True, user