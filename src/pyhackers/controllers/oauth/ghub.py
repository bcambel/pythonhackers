import urllib
from flask.ext.login import login_user
from rauth.service import OAuth2Service
from pyhackers.config import config
from flask import url_for, redirect, request, Blueprint, jsonify
import requests
from model.user import SocialUser, User
from db import DB as db

github_bp = Blueprint('github', __name__)

github = OAuth2Service(name='github',
                       authorize_url='https://github.com/login/oauth/authorize',
                       access_token_url="https://github.com/login/oauth/access_token",
                       client_id=config.get("github", 'client_id'),
                       client_secret=config.get("github", 'client_secret'))


@github_bp.route('/oauth/github')
def login():

    redirect_uri = urllib.quote("http://localhost:5001/oauth/github/authorized")

    return redirect(github.get_authorize_url()) #**params))


@github_bp.route('/oauth/github/authorized')
def authorized():
    # redirect_uri = url_for('authorized', _external=True)
    redirect_uri = "http://dev.pythonhackers.com/oauth/github/authorized"

    # data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    r = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': config.get("github", 'client_id'),
        'client_secret': config.get("github", 'client_secret'),
        'code': request.args['code'],
        'redirect_uri': redirect_uri
    }, headers={"Accept": 'application/json'})

    print r.text
    print r.json
    # response_data = (url_decode(r.text))
    response_data = r.json()

    access_token = response_data['access_token']

    user_data = requests.get("https://api.github.com/user", params=dict(access_token=access_token))

    user_info = user_data.json()

    from github import Github


    g = Github(access_token,
               client_id=config.get("github", 'client_id'),
               client_secret=config.get("github", 'client_secret'), per_page=100)

    # user = g.get_user("mitsuhiko")

    user_login = user_info.get("login")

    social_account = SocialUser.query.filter_by(nick=user_login, acc_type='gh').first()

    user = User.query.filter_by(nick=user_login).first()

    if user is not None:
        login_user(user)

    if social_account is None:
        u = User()
        u.nick = user_login
        u.email = user_info.get("email", "")
        u.pic_url = user_info.get("avatar_url")

        su = SocialUser()
        su.user_id = u.id
        su.nick = user_login
        su.acc_type = 'gh'
        su.email = user_info.get("email","")
        su.follower_count = user_info.get("followers")
        su.following_count = user_info.get("following")
        su.blog = user_info.get("blog")
        su.ext_id = user_info.get("id")
        su.name = user_info.get("name")
        su.hireable = user_info.get("hireable", False)
        su.access_token = access_token
        u.social_accounts.append(su)

        db.session.add(u)
        db.session.commit()

        login_user(u)

    # starred = user.get_starred()
    # for s in starred:
    #     print s.full_name, s.watchers

    # pub_events = user.get_public_events()

    # for e in pub_events:
    #     print e.id, e.type, e.repo.full_name

    return jsonify(user_info) #, response_data.get("access_token")
