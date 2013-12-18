from pyhackers.config import config
import requests
import logging
import time
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.db import DB as db
from sqlalchemy.exc import IntegrityError

client_id = config.get("github", 'client_id')
client_secret = config.get("github", 'client_secret')

url = 'https://api.github.com'
read_me_url = '/repos/{user}/{repo}/readme'

fields = ['id', 'name', 'full_name', 'description', 'owner', 'html_url', 'git_url', 'watchers_count', 'forks_count',
          'open_issues_count', 'created_at', 'updated_at']

session = requests.Session()


def search_repo(query, page=1):
    qs = 'q=%s&sort=stars&per_page=100&page=%d&order=desc&client_id=%s&client_secret=%s' % (
        query, page, client_id, client_secret)
    data = session.get(url + "/search/repositories",
                       params=qs,
                       # params={'q': query, 'sort': 'stars', 'order': 'desc',
                       #         'client_id': client_id, 'client_secret': client_secret},
                       headers={'Accept': 'application/vnd.github.preview'})

    return data.json().get('items', None)


def importer(query, parent=None, exclude=None):
    for i in range(1, 11):
        popular_projects = search_repo(query, i)
        if popular_projects is None or len(popular_projects) <= 0:
            break

        for i, project in enumerate(popular_projects):
            if project is None:
                break

            logging.warn("%d. %s %s %s" % (i, project[fields[1]], project[fields[7]], project[fields[8]]))
            os_proj = OpenSourceProject()
            os_proj.name = project["name"]
            slug = project.get("full_name", str(int(time.time())))

            if parent is not None and (slug == parent or (exclude is not None and slug in exclude)):
                continue

            os_proj.slug = slug
            os_proj.description = project.get('description', '')
            os_proj.watchers = project['watchers_count']
            os_proj.stars = project['watchers_count']
            os_proj.src_url = project['html_url']
            os_proj.git_url = project['git_url']
            os_proj.parent = parent
            db.session.add(os_proj)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

                proj = OpenSourceProject.query.filter_by(slug=slug).first()
                proj.watchers = project['watchers_count']
                proj.parent = parent
                proj.stars = project['watchers_count']

                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()


python_search = '+language:python'
django_search = 'django+language:python'
flask_search = 'flask+language:python'


def import_repos():
    try:
        importer(python_search)
    finally:
        pass
    try:
        importer(django_search, 'django/django', ['django/django-old'])
    finally:
        pass
    try:
        importer(flask_search, 'mitsuhiko/flask')
    finally:
        pass



