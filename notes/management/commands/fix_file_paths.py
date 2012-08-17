from django.core.management.base import BaseCommand
from notes.models import File
from settings import MEDIA_ROOT
import os
from optparse import make_option

# Many old upload locations copied to /var/www/uploads
# /var/www/djKarma/uploads/notes
# /var/www/beta/uploads/notes

# Beta AJAX uploader goes here:
# /var/www/beta/uploads/uploads

# NO such file or dir:
# /var/www/beta/uploads/uploads/notes/Main_Ideas_-_Study_Guide_1.doc
# ACTUALLY IN
# /var/www/beta/uploads/notes


class Command(BaseCommand):
    args = 'none'
    help = 'Attempt to fix File.file paths'
    option_list = BaseCommand.option_list + (
        make_option('--execute',
            action='store_true',
            help='save changes to database'),
    )

    def handle(self, *args, **options):
        do_execute = options.get('execute')
        length = len(File.objects.all())
        count = 0

        for aFile in File.objects.all():
            do_save = False

            try:
                test_file = open(aFile.file.path)
            except IOError:
                # Database file path is incorrect
                fileName, fileExtension = os.path.splitext(aFile.file.path)
                try:
                    test_file = open(os.path.join(MEDIA_ROOT, fileName))
                    File.file = test_file
                    do_save = True
                except IOError:
                    print "Can't find file at " + MEDIA_ROOT + "/" + fileName
            if do_save and do_execute:
                count += 1
                aFile.save()

        self.stdout.write('Corrected file locations for %d / %d files\n' % (count, length))
