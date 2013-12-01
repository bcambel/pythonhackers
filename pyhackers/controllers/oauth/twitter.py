#import urllib
#from flask import url_for, request, session, redirect, Blueprint
#from pyhackers.config import config
#from rauth.service import OAuth1Service
#from rauth.utils import parse_utf8_qsl
#from werkzeug.urls import url_encode
#
#twitter_bp = Blueprint('register', __name__, template_folder='templates')
#
#twitter = OAuth1Service(name='twitter',
#                        request_token_url='https://api.twitter.com/oauth/request_token',
#                        access_token_url='https://api.twitter.com/oauth/access_token',
#                        authorize_url='https://api.twitter.com/oauth/authorize',
#                        base_url='https://api.twitter.com/1/',
#                        consumer_key=config.get("twitter", 'client_id'),
#                        consumer_secret=config.get("twitter", 'client_secret')
#)
#
#
## @twitter.tokengetter
## def get_twitter_token(token=None):
##     return session.get('twitter_token')
#
#
#@twitter_bp.route('/oauth/twitter')
#def login():
#    print config.get("twitter", 'client_id')
#    print config.get("twitter", 'client_secret')
#    oauth_callback = urllib.quote("http://localhost:5001/oauth/twitter/authorized")  #url_for('authorized', _external=True)
#    print oauth_callback
#    params = {'oauth_callback': oauth_callback}
#
#    r = twitter.get_raw_request_token(params=params)
#    data = parse_utf8_qsl(r.content)
#    print data
#
#    session['twitter_oauth'] = (data['oauth_token'],
#                                data['oauth_token_secret'])
#    return redirect(twitter.get_authorize_url(data['oauth_token'], **params))
#
#
#
#
#@twitter_bp.route('/oauth/twitter/authorized')
#def authorized():
#    # next_url = request.args.get('next') or url_for('index')
#    request_token, request_token_secret = session.pop('twitter_oauth')
#
#    # check to make sure the user authorized the request
#    if not 'oauth_token' in request.args:
#        print 'You did not authorize the request'
#        return redirect(url_for('index'))
#
#    try:
#        creds = {'request_token': request_token,
#                'request_token_secret': request_token_secret}
#        params = {'oauth_verifier': request.args['oauth_verifier']}
#        sess = twitter.get_auth_session(params=params, **creds)
#    except Exception, e:
#        print 'There was a problem logging into Twitter: ' + str(e)
#        return redirect(url_for('index'))
#
#    verify = sess.get('account/verify_credentials.json',
#                    params={'format':'json'}).json()
#
#    print verify
#
#    print 'Logged in as ' + verify['name']
#    return redirect(url_for('index'))
#
#    # session['twitter_token'] = (
#    #     resp['oauth_token'],
#    #     resp['oauth_token_secret']
#    # )
#    # session['twitter_user'] = resp['screen_name']
#
#    # flash('You were signed in as %s' % resp['screen_name'])
#    # return redirect(next_url)