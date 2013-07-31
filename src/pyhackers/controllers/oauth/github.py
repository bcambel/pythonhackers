import urllib
from rauth.service import OAuth2Service
from pyhackers.config import config
from flask import url_for, redirect, request, Blueprint, jsonify
import requests
from werkzeug.urls import url_decode

github_bp = Blueprint('github', __name__, template_folder='templates')

github = OAuth2Service(name='github',
                       authorize_url='https://github.com/login/oauth/authorize',
                       access_token_url="https://github.com/login/oauth/access_token",
                       client_id=config.get("github", 'client_id'),
                       client_secret=config.get("github", 'client_secret')
)


@github_bp.route('/oauth/github')
def login():
    # redirect_uri = url_for('authorized', _external=True)
    redirect_uri = urllib.quote("http://localhost:5001/oauth/github/authorized")
    # params = {'redirect_uri': redirect_uri}
    return redirect(github.get_authorize_url()) #**params))


@github_bp.route('/oauth/github/authorized')
def authorized():
    # redirect_uri = url_for('authorized', _external=True)
    redirect_uri = urllib.quote("http://localhost:5001/oauth/github/authorized")

    data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    r = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': config.get("github", 'client_id'),
        'client_secret': config.get("github", 'client_secret'),
        'code': request.args['code'],
    }, )

    response_data =  (url_decode(r.text))

    access_token = response_data['access_token']
    user_data = requests.get("https://api.github.com/user",params=dict(access_token=access_token))

    user_info = user_data.json()
    return jsonify(user_info) #, response_data.get("access_token")
