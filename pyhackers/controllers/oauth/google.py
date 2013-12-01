from json import loads,dumps
import requests
from flask import url_for, request, session, redirect,Blueprint
from flask_oauth import OAuth
from flask.ext.login import login_user
from pyhackers.app import app
from pyhackers.config import config
from pyhackers.models import User

google_bp = Blueprint('register', __name__,template_folder='templates')

oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params= {'scope': 'https://www.googleapis.com/auth/userinfo.email \
                          https://www.googleapis.com/auth/userinfo.profile',
                                                 'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=config.get("google",'client_id'),
                          consumer_secret=config.get("google",'client_secret')
)


@google.tokengetter
def get_access_token():
    return session.get('google_token')



@google_bp.route('/login/google')
def login_google():
    session['next'] = request.args.get('next') or request.referrer or None
    callback=url_for('google_callback', _external=True)
    return google.authorize(callback=callback)


@google_bp.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def google_callback(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        headers={'Authorization': 'OAuth ' + access_token}
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                         headers=headers)
        if r.ok:
            data = loads(r.text)
            oauth_id = data['id']
            user = User.load(oauth_id) or User.add(**data)
            login_user(user)
            next_url = session.get('next') or url_for('index')
            return redirect(next_url)
    return redirect(url_for('login'))




