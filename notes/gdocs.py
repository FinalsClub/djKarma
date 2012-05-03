#gdocs.py
# Copyright (C) 2012  FinalsClub Foundation
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#Dependencies
#gdata
#pymongo
import gdata.sample_util
import gdata.docs.client
import gdata.docs.service
import gdata.docs.data
import gdata.data
import mimetypes
from credentials import GOOGLE_USER, GOOGLE_PASS


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


# Upload File and download html representation
# using Google Documents API v3
def convertWithGDocsv3(File):
    # Create and Authorize OAuth client
    client = CreateClient()

    # Get file_type and encoding of uploaded file
    # i.e: file_type = 'text/plain', encoding = None
    (file_type, encoding) = mimetypes.guess_type(File.file.path)

    # Raise Exception if file has no extension
    if file_type == None:
        raise Exception('File extension required.')

    # Encapsulate File in Google's MediaSource Object
    media = gdata.data.MediaSource()
    media.SetFileHandle(File.file.path, file_type)

    # Create a Resource to connect MediaSource to
    doc = gdata.docs.data.Resource(type='document', title=File.title)

    # Upload document and retrieve representation
    doc = client.CreateResource(entry=doc, media=media)

    # If file is of type that Google can convert to html, download it
    if file_type == "plain/text" or file_type == "application/msword":
        # Download html representation of document
        client.download_resource(entry=doc, file_path=File.file.path + '.html')

        f = open(str(File.file.path) + '.html')
        File.html = f.read()
        File.save()
        f.close()
    # If pdf, we can use Google Document iframe to view
    elif file_type == "application/pdf":
        File.html = "pdf"
        File.save()



# Upload File and download html representation
# using Google Documents API v2
# Works. Lacks pdf support
def convertWithGDocs(File):
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
    #	print doc




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
