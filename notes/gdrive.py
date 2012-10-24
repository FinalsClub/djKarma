# coding: utf-8
import httplib2
from oauth2client.client import flow_from_clientsecrets

CLIENT_SECRET = './notes/client_secrets.json'
#from credentials import GOOGLE_USER
GOOGLE_USER = 'seth.woodworth@gmail.com'

def build_flow():
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ]

    flow = flow_from_clientsecrets(CLIENT_SECRET, ' '.join(SCOPES), redirect_uri='http://localhost:8000/oauth2callback')
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = GOOGLE_USER
    return flow


def authorize():
    flow = build_flow()
    print flow.step1_get_authorize_url()

def accept_auth(code):
    flow = build_flow()
    creds = flow.step2_exchange(code)
    return creds


