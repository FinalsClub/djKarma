"""
Index descriptions to make various models searchable.
"""
from haystack.indexes import *
from haystack.fields import EdgeNgramField
from haystack import site
from models import School, Course, File


class SchoolIndex(SearchIndex):
    # documenet=True indicates this is the primary search field

    # use_template allows us to specify a django-style template
    # containing all the relevant text for a School
    # without use_template=True Haystack concatenates all the fields
    # which apparently can be undesirable
    # See ./KNotes/templates/search/indexes/notes/school_text.txt
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='name')

    # Example custom queryset for objects to add to index
    # For Schools, we'll index the complete set
    '''
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Note.objects.filter(pub_date__lte=datetime.datetime.now())
    '''


class CourseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='title')

    # Non document fields allow for search filtering
    # i.e: Search "math" at school Harvard
    title = CharField(model_attr='title')
    school = CharField(null=True)
    semester = IntegerField(model_attr='semester')
    academic_year = IntegerField(model_attr='academic_year')

    # When the index is prepared, index
    # the pk corresponding to this course's school
    def prepare_school(self, obj):
        if obj.school is not None:
            return obj.school.pk

        return None


class FileIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title')
    school = CharField(null=True)
    corse = CharField(null=True)

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='title')

    # When the index is prepared, index
    # the pk corresponding to this file's school
    def prepare_school(self, obj):
        if obj.school is not None:
            return obj.school.pk

        return None

    # Store the pk of the corresponding course
    def prepare_course(self, obj):
        if obj.course is not None:
            return obj.course.pk

        return None

    '''
    # Use Apache Solr's Rich Content Extraction
    # To index document text for search
    def prepare(self, obj):
        data = super(FileIndex, self).prepare(obj)
        try:
            # This could also be a regular Python open() call, a StringIO instance
            # or the result of opening a URL. Note that due to a library limitation
            # file_obj must have a .name attribute even if you need to set one
            # manually before calling extract_file_contents:
            file_obj = obj.file.open()

            extracted_data = self.backend.extract_file_contents(file_obj)

            # Now we'll finally perform the template processing to render the
            # text field with *all* of our metadata visible for templating:
            t = loader.select_template(('search/indexes/notes/file_text.txt', ))
            data['text'] = t.render(Context({'object': obj,
                                             'extracted': extracted_data}))
        except IOException:
            print "FileIndex: error accessing " + obj.file.path
            # actual file is not available
        return data
    '''

site.register(File, FileIndex)
site.register(School, SchoolIndex)
site.register(Course, CourseIndex)
