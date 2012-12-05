from celery.task import task
from gdocs import convertWithGDocsv3
from notes.gdrive import convert_with_google_drive

@task
def processDocument(File):
    """ Process file with the Google Documents API,
        populating File.html with Google's response

        Returns True on success, else False
    """
    print "processing document"
    try:
        # Switch to GDrive integration here
        convertWithGDocsv3(File)
    except Exception, e:
        print "Error processing document: " + str(e)
        return False
    return True

@task
def process_document(a_file):
    """ Process a file with Google Drive
        populates and saves the File.html, File.text
        or if a pdf, File.is_pdf and File.embed_url
        for either, it saves a File.gdrive_url

        :a_file: A `models.File` instance associated, document or pdf file
        :returns: True on success, else False
    """
    print "Processing document: %s -- %s" % (a_file.id, a_file.title)
    try:
        convert_with_google_drive(a_file)
    except Exception, e:
        print "\terror processing doc: %s -- %s" % (a_file.id, a_file.title)
        return False
    return True
