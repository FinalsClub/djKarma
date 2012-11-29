#!/usr/bin/python2.7
# -*- coding:utf8 -*-
""" Copyright (C) 2012  FinalsClub Foundation """

import datetime
import mimetypes
import os

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets

from notes.models import DriveAuth

CLIENT_SECRET = './notes/client_secrets.json'
#from credentials import GOOGLE_USER
GOOGLE_USER = 'seth.woodworth@gmail.com'
EXT_TO_MIME = {'.docx': 'application/msword'}

def build_flow():
    """ Create an oauth2 autentication object with our preferred details """
    scopes = [
        'https://www.googleapis.com/auth/drive',
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


def build_api_service(creds):
    http = httplib2.Http()
    http = creds.authorize(http)
    return build('drive', 'v2', http=http)


def check_and_refresh(creds, auth, http):
    """ Check a Credentials object's expiration token
        if it is out of date, refresh the token and save
        :creds: a Credentials object
        :auth:  a DriveAuth that backs the cred object
        :http:  authenitcated httplib2 session
        :returns: updated creds and auth objects
    """
    if creds.token_expiry < datetime.datetime.utcnow():
        # if we are passed the token expiry, 
        # refresh the creds and store them
        http = httplib2.Http()
        http = creds.authorize(http)
        creds.refresh(http)
        auth.credentials = creds.to_json()
        auth.save()
    return creds, auth


def list_files(http):
    """ list the google drive files uploaded via this session/cred
        :http:  authenticated httplib2 instance
        :returns: list of files
    """
    return service.files().list().execute()


def convert_with_google_drive(u_file):
    """ Upload a local u_file and download HTML
        using Google Drive
        :u_file: a u_file model instance
    """
    # Get file_type and encoding of uploaded file
    # i.e: file_type = 'text/plain', encoding = None
    (file_type, encoding) = mimetypes.guess_type(u_file.file.path)

    # If mimetype cannot be guessed
    # Check against known issues, then
    # finally, Raise Exception
    # Extract file extension and compare it to EXT_TO_MIME dict

    fileName, fileExtension = os.path.splitext(u_file.file.path)

    if file_type == None:

        if fileExtension.strip().lower() in EXT_TO_MIME:
            file_type = EXT_TO_MIME[fileExtension.strip().lower()]
        # If boy mimetypes.guess_type and EXT_TO_MIME fail to cover
        # file, return error
        else:
            raise Exception('Unknown file type')

    resource = {
                'title':    u_file.title,
                'desc':     u_file.description,
                'mimeType': file_type
            }
    # TODO: set the permission of the file to permissive so we can use the 
    #       gdrive_url to serve files directly to users
    media = MediaFileUpload(u_file.file.path, mimetype=file_type,
                chunksize=1024*1024, resumable=True)

    auth = DriveAuth.objects.filter(email=GOOGLE_USER).all()[0]
    creds = auth.transform_to_cred()

    service = build_api_service(creds)

    creds, auth = check_and_refresh(creds, auth, http=service)

    # Upload the file
    # TODO: wrap this in a try loop that does a token refresh if it fails
    print "Trying to upload document"
    file_dict = service.files().insert(body=resource, media_body=media, convert=True).execute()

    # set u_file.is_pdf
    if file_type == 'application/pdf':
        # If it's a pdf, instead save an embed_url from resource['selfLink']
        u_file.is_pdf = True
        u_file.embed_url = file_dict[u'selfLink']
        u_file.gdrive_url = file_dict[u'downloadUrl']
    else:
        # get the converted filetype urls
        download_urls = {}
        download_urls['html'] = file_dict[u'exportLinks']['text/html']
        download_urls['text'] = file_dict[u'exportLinks']['text/plain']
        # set the .odt as the download from google link
        u_file.gdrive_url = file_dict[u'exportLinks']['application/vnd.oasis.opendocument.text']

        h = httplib2.Http('')
        for download_type, download_url in download_urls.items():
            resp, content = h.request(download_url, "GET")

            if resp.status in [200]:
                # save to the File.property resulting field
                u_file.__dict__[download_type] = content

    # Finally, save whatever data we got back from google
    u_file.save()


if __name__=='__main__':
    print "You have to run this via ./manage.py shell, which is rediculous."
