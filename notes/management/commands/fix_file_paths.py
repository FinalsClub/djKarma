from django.core.management.base import BaseCommand
from notes.models import File
from django.core.files import File as djangoFile
from KNotes.settings import MEDIA_ROOT
import os
from optparse import make_option
from django.core.exceptions import SuspiciousOperation

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
        files = File.objects.all()

        for aFile in files:
            do_save = True

            try:
                self.stdout.write("\n")
                self.stdout.write("file id: %s \n" % (aFile.id))
                # uploads/notes/Main_Ideas_-_Study_Guide_1.doc
                self.stdout.write("file path: %s \n" % (aFile.file.name))
                fileName = os.path.basename(aFile.file.name)
                self.stdout.write("> file name: %s \n" % (fileName))
                proper_file_path = os.path.join(MEDIA_ROOT, fileName)
                self.stdout.write("> trying: %s \n" % (proper_file_path))
                # Attempt to find this filename in MEDIA_ROOT
                # If success, update filefield entry
                proper_file = open(proper_file_path)
                #Just in case file.save mutates db
                if do_execute:
                    #aFile.file.save(fileName, djangoFile(proper_file), save=True)
                    setattr(aFile.file, 'name', proper_file_path)
                self.stdout.write("> success! new filepath set \n")
                if not (do_save and do_execute):
                    count += 1
                #test_file = open(aFile.file.file.path)
            except (IOError, SuspiciousOperation) as e:
                self.stdout.write("> error: %s \n" % (str(e)))
                # Database file path is incorrect
            if do_save and do_execute:
                count += 1
                aFile.save()

        self.stdout.write('Corrected file locations for %d / %d files\n' % (count, length))
