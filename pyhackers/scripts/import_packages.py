from __future__ import print_function
import logging
import simplejson
from os import listdir
from os.path import join, isfile
from pyhackers.config import config
from pyhackers.model.package import Package
from pyhackers.db import DB as db
import codecs

package_directory = '/Users/bahadircambel/code/learning/pythonhackers/packages'


def import_package(package_dict):
    inf = package_dict['info']
    p = Package()
    p.name = inf.get('name')
    p.summary = inf.get('summary', "")
    p.description = inf.get('description', "")
    #p.version = inf.get('version')
    p.author = inf.get('author', "")
    p.author_email = inf.get('author_email', "")
    p.url = inf.get("home_page", "")
    downloads = inf.get("downloads")
    p.mdown = downloads.get("last_month")
    p.wdown = downloads.get("last_week")
    p.ddown = downloads.get("last_day")

    p.data = ""
    #p.data = package_dict
    #try:
    #logging.warn(u"{name}-{version}-{mdown},{wdown},{ddown}-{url}-{summary}".format(p.__dict__))
    #except Exception,ex:
     #   logging.exception(ex)
    db.session.add(p)
    try:
        db.session.commit()
    except Exception, ex:
        db.session.rollback()
        logging.exception(ex)




def find_files(directory):
    files = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]

    for file in files:
        try:
            lines = codecs.open(file, "r", "utf-8").readlines()
            json_file = u" ".join(lines)
            data = simplejson.loads(json_file)
            import_package(data)
        except Exception,ex:
            logging.warn(u"Exception for {} - {}".format(file, ex))
            logging.exception(ex)
            raise ex



#find_files(package_directory)
# from pyhackers.app import start_app;start_app();from pyhackers.scripts.import_packages import *;find_files(package_directory)