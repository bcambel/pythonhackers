from pyhackers.config import config
import requests
import logging

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


def printer():
    for i in range(1, 11):
        popular_projects = search_repo('+language:python', i)

        for i, project in enumerate(popular_projects):
            logging.warn("%d. %s %s %s" % (i, project[fields[1]], project[fields[7]], project[fields[8]]))

# django_projects = search_repo('django')
# python_projects = search_repo('python')
# flask_projects = search_repo('flask')



