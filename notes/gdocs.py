#!/usr/bin/python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

#Dependencies
#gdata
#pymongo

import mimetypes
import os

import gdata.sample_util
import gdata.docs.client
import gdata.docs.service
import gdata.docs.data
import gdata.data

from credentials import GOOGLE_USER, GOOGLE_PASS

# A dictionary containing known extensions missed by mimetypes.guess_type
EXT_TO_MIME = {'.docx': 'application/msword'}

###################################
#### Google Docs API V3 Helpers ###
###################################

class SampleConfig(object):
    APP_NAME = 'Karma Notes'
    DEBUG = False


def CreateClient():
    """Create a Documents List Client."""
    client = gdata.docs.client.DocsClient(source=SampleConfig.APP_NAME)
    client.http_client.debug = SampleConfig.DEBUG
    client.client_login(GOOGLE_USER, GOOGLE_PASS, source=client.source, service=client.auth_service)
    return client

#######################################
#### End Google Docs API V3 Helpers ###
#######################################


def convertWithGDocsv3(File):
    """ Upload File and download html representation
        using Google Documents API v3
    """
    # Create and Authorize OAuth client
    client = CreateClient()
    print "GDocsv3: client created"
    # Create a dictionary for extra Google query variables
    query_args = {'exportFormat': 'html'}

    # Get file_type and encoding of uploaded file
    # i.e: file_type = 'text/plain', encoding = None
    (file_type, encoding) = mimetypes.guess_type(File.file.path)

    # If mimetype cannot be guessed
    # Check against known issues, then
    # finally, Raise Exception
    # Extract file extension and compare it to EXT_TO_MIME dict

    fileName, fileExtension = os.path.splitext(File.file.path)

    if file_type == None:

        if fileExtension.strip().lower() in EXT_TO_MIME:
            file_type = EXT_TO_MIME[fileExtension.strip().lower()]
        # If boy mimetypes.guess_type and EXT_TO_MIME fail to cover
        # file, return error
        else:
            raise Exception('Unknown file type')

    # Encapsulate File in Google's MediaSource Object
    media = gdata.data.MediaSource()
    media.SetFileHandle(File.file.path, file_type)
    print "GDocsv3: MediaSource created"
    # Create a Resource to connect MediaSource to
    if File.title:
        file_title = File.title
    else:
        # If the django File obj has no title
        # Use the filename. This only affects the document
        # name in Karma Note's Google Docs account
        file_title = fileName.rsplit("/", 1)[1]
    doc = gdata.docs.data.Resource(type='document', title=file_title)
    print "GDocsv3: resource created"
    # if pdf, append OCR=true to uri
    if file_type == 'application/pdf':
        create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI + '?ocr=true'
    else:
        create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI

    # Upload document and retrieve representation
    doc = client.CreateResource(entry=doc, create_uri=create_uri, media=media)
    print "GDocsv3: resource sent"
    print "file_type: " + str(file_type)

    # Download html representation of document
    client.download_resource(entry=doc, file_path=File.file.path + '.html', extra_params=query_args)
    print "GDocsv3: resource downloaded"
    f = open(str(File.file.path) + '.html')
    File.html = f.read()
    File.save()
    f.close()


def convertWithGDocs(File):
    """ Upload File and download html representation
        using Google Documents API v2
        Works. Lacks pdf support
    """
    #print Note.file.path
    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.docs.service.DocsService()
    # Authenticate using your Google Docs email address and password.
    client.ClientLogin(GOOGLE_USER, GOOGLE_PASS)

    (file_type, encoding) = mimetypes.guess_type(File.file.path)
    # file_type = 'text/plain', encoding = None

    if file_type == None:
        raise Exception('File extension required.')

    #Encapsulate the upload file as Google requires
    fileToUpload = gdata.data.MediaSource(file_path=File.file.path, content_type=file_type)

    #Create a collection (folder) in the root directory
    #collection = client.CreateFolder(title='API Generated Folder')

    #Create a collection within the previously created collection
    #collection_child = client.CreateFolder(title='API Generated Folder Child', folder_or_uri=collection)
    #You can also specify the folder by it's Resource Id:
    #collection_child = client.CreateFolder(title='API Generated Folder Child', folder_or_uri='/feeds/folders/private/full/folder%3A0B0_WBOXykQApLU1EaFNlM1dRQXVTM2tEdVFudXpaZw')

    #Upload a document to a folder
    #uploaded_file = client.Upload(media_source=fileToUpload, title=Note.title, folder_or_uri=collection_child)
    uploaded_file = client.Upload(media_source=fileToUpload, title=File.title)
    client.Download(entry_or_id_or_url=uploaded_file, file_path=File.file.path + '.html')
    f = open(File.file.path + '.html')
    File.html = f.read()
    File.save()
    f.close()
    #document_query = gdata.docs.service.DocumentQuery()
    #print document_query.ToUri()
    #documents_feed = client.GetDocumentListFeed()
    #for doc in documents_feed.entry:
    #   print doc




    #client._DownloadFile('https://docs.google.com/feeds/download/documents/Export?docId=0AU_WBOXykQApZGZ3cWdtcGRfNDg3enJtdg','/Users/dbro/Documents/test.html')
    # Query the server for an Atom feed containing a list of your documents.
    #documents_feed = client.GetDocumentListFeed()

    #print documents_feed[0]
    # Loop through the feed and extract each document entry.
    #for document_entry in documents_feed.entry:
      # Display the title of the document on the command line.
      #xml = xml.dom.minidom.parseString(str(document_entry))
      #toPrint = xml.toprettyxml()
      #print str(document_entry)
