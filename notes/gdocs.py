#gdocs.py

#Dependencies
#gdata
#pymongo
import gdata.docs.service
import gdata.docs.data
import gdata.data
import mimetypes
from credentials import USER, PASS
from KNotes.settings import MEDIA_ROOT


# given a filePath, upload the file to Google Docs and retrieve html
def convertWithGDocs(Note):
    #print Note.file.path
    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.docs.service.DocsService()
    # Authenticate using your Google Docs email address and password.
    client.ClientLogin(USER, PASS)

    (file_type, encoding) = mimetypes.guess_type(Note.file.path)
    # file_type = 'text/plain', encoding = None

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

def UploadResourceSample():
  """Upload a document, and convert to Google Docs."""
  doc = gdata.docs.data.Resource(type='document', title='My Sample Doc')
  # This is a convenient MS Word doc that we know exists
  path = _GetDataFilePath('test.0.doc')
  print 'Selected file at: %s' % path
  # Create a MediaSource, pointing to the file
  media = gdata.data.MediaSource()
  media.SetFileHandle(path, 'application/msword')
  # Pass the MediaSource when creating the new Resource
  doc = client.CreateResource(entry=doc, media=media)
  print 'Created, and uploaded:', doc.title.text, doc.resource_id.text
