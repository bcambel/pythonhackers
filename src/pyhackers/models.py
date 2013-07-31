import logging
from setup import mc


log = logging.getLogger("")


class User(object):

    def __init__(self, *args, **kwargs):
        self.id = None
        self.username = None
        self.permissions = []

        self.id = kwargs.get("id",kwargs.get("username",None)) or None
        self.username = kwargs.get("username") or None


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def has_permission(self, level):
        logging.warn("User has %s in %r" % (level, self.permissions))
        for perm_dict in self.permissions:
            slug = perm_dict.get("slug", "")

            logging.warn("(%s) vs (%s)" % (slug, level))

            if slug == level:
                logging.warn("User has the permission[%s]" % level)
                return True

        return False

    def __str__(self):
        return  self.username

    def __unicode__(self):
        return self.__str__()

    @classmethod
    def load(cls, oauth_id):
        pass

    @classmethod
    def add(cls, param):
        pass


class UserStore(object):

    def __init__(self, instance_slug,mc_client):
        self.instance_slug = instance_slug
        self.mc_client = mc_client

    def get_key(self,user_id):
        return str("%s-%s" % (self.instance_slug, user_id))

    def get(self, user_id):
        data = None

        try:
            data = self.mc_client.get(self.get_key(user_id))
            log.debug("Found data for %s => %s" % (user_id, data))
        except Exception,ex:
            log.exception(ex)
            log.error("Failed to read data from Memcache")

        return data

    def set(self, user_id, data):
        try:
            return self.mc_client.set( self.get_key(user_id), data )
        except Exception,ex:
            log.exception(ex)
            return False

    def remove(self, user_id):
        try:
            return self.mc_client.delete(self.get_key(user_id))
        except Exception,ex:
            log.exception(ex)
            return False


def init_store( inst_slug):
    userStorage = UserStore(inst_slug,mc)
    return userStorage