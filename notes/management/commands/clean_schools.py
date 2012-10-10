from django.core.management.base import BaseCommand
from notes.models import School
from django.template.defaultfilters import slugify


class Command(BaseCommand):
    args = 'none'
    help = ('Ensures Schools have slugs, generates them if not')

    def handle(self, *args, **options):
        length = len(School.objects.all())
        count = 0  # Count of models affected by this command
        for school in School.objects.all():
            do_save = False
            if school.slug == None:
                school.slug = slugify(school.name)
                do_save = True
                self.stdout.write('Populated slug for  %s \n' % school.name)

            if do_save:
                count += 1
                school.save()

        self.stdout.write('Populated default values for %d / %d schools\n' % (count, length))

