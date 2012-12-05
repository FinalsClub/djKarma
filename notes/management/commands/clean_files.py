from django.core.management.base import BaseCommand
from notes.models import File, Course, School

class Command(BaseCommand):
    args = 'none'
    help = ('cleanup files by adding missing course and school to the model')

    def handle(self, *args, **kwargs):
        files = File.objects.all()
        for f in files:
            if ff.course:
                ff.school = ff.course.school
                ff.save()
            # TODO implement other file cleanups
