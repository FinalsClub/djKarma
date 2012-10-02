from django.core.management.base import BaseCommand
from notes.models import School, Course

class Command(BaseCommand):
    args = 'none'
    help = ('Populates Courses with default School, semester, academic_year info if None. '
            'Also enforces uniqueness of (school, slug). ')

    def handle(self, *args, **options):
        length = len(Course.objects.all())
        count = 0  # Count of models affected by this command
        duplicate_courses = []  # List of pk tuples corresponding to Courses with (school, slug) collision
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

        for course in Course.objects.all():
            for other_course in Course.objects.all():
                    if course.slug == other_course.slug and course.school == other_course.school and course.pk != other_course.pk:
                        if (course.pk, other_course.pk) not in duplicate_courses and (other_course.pk, course.pk) not in duplicate_courses:
                            duplicate_courses.append((course.pk, other_course.pk))
                            self.stdout.write('Duplicate courses:  %s and %s titled: %s \n' % (course.pk, other_course.pk, course.slug))

        self.stdout.write('Found %d duplicate courses \n' % len(duplicate_courses))
