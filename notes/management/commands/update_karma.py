from django.core.management.base import BaseCommand
from notes.models import Course, School

class Command(BaseCommand):
    args = 'none'
    help = ('update the karma value for all schools')

    def handle(self, *args, **kwargs):
    	schools = School.objects.all()
    	for school in schools:
    		school.sum_karma()

    	


