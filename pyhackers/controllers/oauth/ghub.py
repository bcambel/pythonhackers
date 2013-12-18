import urllib
from flask.ext.login import login_user
from pyhackers.service.user import create_user_from_github_user
from rauth.service import OAuth2Service
from pyhackers.config import config
from flask import url_for, redirect, request, Blueprint, jsonify
import requests
from pyhackers.model.user import SocialUser, User
from pyhackers.db import DB as db
import logging

github_bp = Blueprint('github', __name__)

github = OAuth2Service(name='github',
                       authorize_url='https://github.com/login/oauth/authorize',
                       access_token_url="https://github.com/login/oauth/access_token",
                       client_id=config.get("github", 'client_id'),
                       client_secret=config.get("github", 'client_secret'))


@github_bp.route('/oauth/github')
def login():
    return redirect(github.get_authorize_url())


@github_bp.route('/oauth/github/authorized')
def authorized():

    redirect_uri = "{}oauth/github/authorized".format(request.host_url)

    logging.warn(redirect_uri)
    r = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': config.get("github", 'client_id'),
        'client_secret': config.get("github", 'client_secret'),
        'code': request.args['code'],
        'redirect_uri': redirect_uri
    }, headers={"Accept": 'application/json'})

    logging.warn(r.json())
    response_data = r.json()

    access_token = response_data['access_token']

    user_data = requests.get("https://api.github.com/user", params=dict(access_token=access_token))

    user_info = user_data.json()

    user = create_user_from_github_user(access_token, user_info)

    if user is not None:
        login_user(user)
        return redirect("/")
    else:
        return redirect("/")


    # return jsonify(user_info) #, response_data.get("access_token")
