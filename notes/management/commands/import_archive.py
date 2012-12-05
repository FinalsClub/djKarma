from django.core.management.base import BaseCommand
from notes.models import School, Course, File, Instructor #(* in dev)
from django.template.defaultfilters import slugify
import json


class Command(BaseCommand):
    args = 'none'
    help = ('imports notes that have been exported in JSON form from a MongoDB')

    def index_archive(self, items):
        new_items = {}
        for item in items:
                item_id = item['id']
                new_items[item_id] = item
        return new_items

    def load_archives(self):
        """ loads json files and returns indexed archives for courses/subjects/notes """
        archives = ['archivedcourses', 'archivedsubjects', 'archivednotes']
        archive_dict = {}
        for archive in archives:
                archive_json = json.loads(open(archive + '.json', 'r').read())
                if archive != 'archivednotes':
                        archive_dict[archive] = self.index_archive(archive_json)
                else:
                        archive_dict[archive] = archive_json
        return archive_dict

    def handle(self, *args, **options):
        archives = self.load_archives()

        # assuming everything is Harvard
        sch = School.objects.filter(name = "Harvard")[0]
        year = 2009

        # first we add the Simplest item required: Instructors
        # we will search for existing ones, and add those who dont exist
        orphanednotes = []
        for note in archives['archivednotes']:
                course_id = note['course_id']
                course = archives['archivedcourses'].get(course_id)
                if course == None:
                        orphanednotes.append(note)
                        continue #if a note does not properly link to a course, we add it to a list, then skip over the note
                subject_id = course['subject_id']
                subject = archives['archivedsubjects'][subject_id]
                temp_instructor, created = Instructor.objects.get_or_create(name=course['instructor'], school=sch)
                if created:
                        self.stdout.write('instructor created')

                # now we look for courses that do not exist, and add them
                course_slug = slugify(course['name'])
                #this is done in a TRY because uniqueness requirements get weird
                try:
                        temp_course, created = Course.objects.get_or_create(slug = course_slug, title = course['name'])
                        if created:
                                self.stdout.write('course created')
                except:
                        self.stdout.write('course already exists')
                #then, once it IS created, we add data.  Otherwise, we assume that its got data attached
                if created:
                        temp_course.school = sch
                        temp_course.field = subject['name']
                        temp_course.academic_year = year
                        temp_course.instructor = temp_instructor
                        temp_course.save()

                # now for actually uploading notes
                temp_note, created = File.objects.get_or_create(title = note['topic'],
                                                                                        description = note['topic'],
                                                                                        course = temp_course,
                                                                                        school = sch,
                                                                                        html = note['text'])
                if created:
                        self.stdout.write('note created')
