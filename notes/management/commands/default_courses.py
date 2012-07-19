from django.core.management.base import BaseCommand
from notes.models import School, Course

class Command(BaseCommand):
    args = 'none'
    help = 'Iterates over Courses and fills null fields with default values, i.e: School, academic_year.'

    def handle(self, *args, **options):
        length = len(Course.objects.all())
        count = 0
        for course in Course.objects.all():
            do_save = False
            if course.academic_year == None:
                course.academic_year = 2012
                do_save = True
                self.stdout.write('Populated academic year for  %s \n' % course.title)
            if course.school == None:
                # if null, set the school to Harvard
                course.school = School.objects.filter(pk=1)[0]
                do_save = True
                self.stdout.write('Populated school for  %s \n' % course.title)
            if course.semester == None:
                course.semester = 1
                do_save = True
                self.stdout.write('Populated semester for  %s \n' % course.title)
            if do_save:
                count += 1
                course.save()

        self.stdout.write('Populated default values for %d / %d courses\n' % (count, length))
