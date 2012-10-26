#!/usr/bin/python2.7
# -*- coding:utf8 -*-
""" Copyright (C) 2012  FinalsClub Foundation """

import httplib2
from oauth2client.client import flow_from_clientsecrets

CLIENT_SECRET = './notes/client_secrets.json'
#from credentials import GOOGLE_USER
GOOGLE_USER = 'seth.woodworth@gmail.com'

def build_flow():
    """ Create an oauth2 autentication object with our preferred details """
    scopes = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ]

    flow = flow_from_clientsecrets(CLIENT_SECRET, ' '.join(scopes), \
            redirect_uri='http://localhost:8000/oauth2callback')
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = GOOGLE_USER
    return flow


def authorize():
    """ Use an oauth2client flow object to generate the web url to create a new
        auth that can be then stored """
    flow = build_flow()
    print flow.step1_get_authorize_url()


def accept_auth(code):
    """ Callback endpoint for accepting the post `authorize()` google drive 
        response, and generate a credentials object
        :code:  An authentication token from a WEB oauth dialog
        returns a oauth2client credentials object """
    flow = build_flow()
    creds = flow.step2_exchange(code)
    return creds

