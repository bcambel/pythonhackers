from pyhackers.config import config
import requests
import logging
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.app import db

client_id = config.get("github", 'client_id'),
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
                       headers={'Accept': 'application/vnd.github.preview'}
    )

    return data.json().get('items', None)

import time
def printer():
    for i in range(1, 11):
        popular_projects = search_repo('+language:python', i)
        if popular_projects is None:
            break
        for i, project in enumerate(popular_projects):
            logging.warn("%d. %s %s %s" % (i, project[fields[1]], project[fields[7]], project[fields[8]]))
            os_proj = OpenSourceProject()
            # os_proj.id = project['id']
            os_proj.name = project["name"]
            os_proj.slug = project.get("full_name",str(int(time.time())))
            os_proj.description = project.get('description', '')[:500]
            os_proj.watchers = project['watchers_count']
            os_proj.stars = project['watchers_count']
            os_proj.src_url = project['html_url']
            os_proj.git_url = project['git_url']

            db.session.add(os_proj)

        db.session.commit()


# django_projects = search_repo('django')
# python_projects = search_repo('python')
# flask_projects = search_repo('flask')



