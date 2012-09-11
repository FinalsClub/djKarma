from celery.task import task
from gdocs import convertWithGDocsv3

@task
def processDocument(File):
    """
        Process file with the Google Documents API,
        populating File.html with Google's response

        Returns True on success, else False
    """
    print "processing document"
    try:
        convertWithGDocsv3(File)
    except Exception, e:
        print "Error processing document: " + str(e)
        return False
    return True
