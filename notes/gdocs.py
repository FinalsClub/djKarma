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
import gdata.docs.service
import gdata.docs.data
import gdata.data
import mimetypes
from credentials import GOOGLE_USER, GOOGLE_PASS
from KNotes.settings import MEDIA_ROOT


# given a filePath, upload the file to Google Docs and retrieve html
def convertWithGDocs(Note):
    #print Note.file.path
    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.docs.service.DocsService()
    # Authenticate using your Google Docs email address and password.
    client.ClientLogin(GOOGLE_USER, GOOGLE_PASS)

    (file_type, encoding) = mimetypes.guess_type(Note.file.path)
    # file_type = 'text/plain', encoding = None

    if file_type == None:
        raise Exception('File extension required.')

    #Encapsulate the upload file as Google requires
    fileToUpload = gdata.data.MediaSource(file_path=Note.file.path, content_type=file_type)

    #Create a collection (folder) in the root directory
    #collection = client.CreateFolder(title='API Generated Folder')

    #Create a collection within the previously created collection
    #collection_child = client.CreateFolder(title='API Generated Folder Child', folder_or_uri=collection)
    #You can also specify the folder by it's Resource Id:
    #collection_child = client.CreateFolder(title='API Generated Folder Child', folder_or_uri='/feeds/folders/private/full/folder%3A0B0_WBOXykQApLU1EaFNlM1dRQXVTM2tEdVFudXpaZw')

    #Upload a document to a folder
    #uploaded_file = client.Upload(media_source=fileToUpload, title=Note.title, folder_or_uri=collection_child)
    uploaded_file = client.Upload(media_source=fileToUpload, title=Note.title)
    client.Download(entry_or_id_or_url=uploaded_file, file_path=Note.file.path+'.html')
    f = open(Note.file.path+'.html')
    Note.html = f.read()
    Note.save()
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
