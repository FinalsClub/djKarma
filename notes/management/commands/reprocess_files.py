from collections import Counter
import os
import time

from django.core.management.base import BaseCommand
from apiclient.errors import HttpError

from notes import tasks
from notes.gdrive import convert_with_google_drive
from notes.models import File

class Timer(object):
    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type, value, traceback):
        self.__finish = time.time()

    def duration_in_seconds(self):
        return self.__finish - self.__start

class Command(BaseCommand):
    """ Django management command to reprocess all locally stored
        documents using the google drive API.
    """
    args = 'none'
    help = 'Reprocess locally stored word documents using google drive'

    def handle(self, *args, **options):
        """ Loop over local model.File objects, regenerate .html and .text """
        counter = Counter()
        full_timer = Timer()
        with full_timer:
            for fp in File.objects.filter(file__isnull=False).all():
                inner_time = Timer()
                with inner_time:
                    # don't try to process files that are HTML only in the db
                    if not os.path.exists(fp.file.path):
                        counter['file paths not found'] += 1
                        continue

                    # Kick off celery task to process document
                    #tasks.process_document.delay(fp)

                    try:
                        # Process the document directly
                        convert_with_google_drive(fp)
                    except HttpError:
                        counter['files errored'] += 1
                    counter['files processed'] += 1

                counter[inner_time.duration_in_seconds()] += 1

        self.stdout.write('\n\n\n')
        self.stdout.write('#' * 40)
        self.stdout.write('\n')
        self.stdout.write('Processing complete')
        self.stdout.write('\n')
        self.stdout.write('Time to completion in seconds:')
        self.stdout.write('\n')
        self.stdout.write('\t %s' % full_timer.duration_in_seconds())


        for string, count in counter.items():
            self.stdout.write('\n')
            self.stdout.write('\t%s:' % string)
            self.stdout.write('\t\t%s' % count)
            self.stdout.write('\n')

        self.stdout.write('\n')
        self.stdout.write('Mean processing time:')
        self.stdout.write('\n')
        try:
            self.stdout.write('\t%s' % counter.most_common(3)[2])
        except:
            self.stdout.write('\t%s' % counter.most_common()[:5])
