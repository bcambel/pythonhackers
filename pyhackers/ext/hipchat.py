import requests
import simplejson as json
from pyhackers.config import config


api_token = config.get("hipchat", "token")


def notify_registration(msg, token=None):
    auth_token = token or api_token
    params = {"message": msg}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    requests.post("https://api.hipchat.com/v2/room/register/notification?auth_token={}".format(auth_token),
                      data=json.dumps(params),
                      headers=headers)
