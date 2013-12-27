import logging
import ConfigParser
import os

logging.basicConfig(format='[%(asctime)s](%(filename)s#%(lineno)d)%(levelname)-7s %(message)s',
                    level=logging.NOTSET)

config = ConfigParser.RawConfigParser()

configfiles = list()

# load default config file
dev_cfg = os.path.join(os.path.dirname(__file__), 'app.local.cfg')
logging.warn("Dev: %s" % dev_cfg)
configfiles += [dev_cfg]

configfiles += ['/var/`']

logging.warn('Configuration files read: %s' % configfiles)

files_read = config.read(configfiles)

logger = logging.getLogger("")

logger.warn('Configuration files read: %s' % files_read)

logger.setLevel(int(config.get('app', 'log_level')))


APPS_TO_RUN = ['web','idgen']

try:
    SENTRY_DSN = config.get("sentry", "dsn")
except Exception as ex:
    logger.error(ex)
    logger.warn("{0}Sentry client is DUMMY now{0} Config=>[{1}]".format(20 * "=", SENTRY_DSN))