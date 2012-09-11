from django.core.management.base import BaseCommand
from notes.models import School, Course, File


class Command(BaseCommand):
    args = 'none'
    help = 'Iterates over Files and fills null fields with default values, i.e: School, course.'

    def handle(self, *args, **options):
        length = len(File.objects.all())
        count = 0
        for file in File.objects.all():
            do_save = False
            if file.school == None:
                file.school = School.objects.get(pk=1)
                do_save = True
                self.stdout.write('Populated school for  %s \n' % (file.title))
            if file.course == None:
                file.course = Course.objects.get(pk=1)
                do_save = True
                self.stdout.write('Populated course for  %s \n' % (file.title))
            if do_save:
                count += 1
                file.save()

        self.stdout.write('Populated default values for %d / %d files \n' % (count, length))
