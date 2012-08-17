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
    school = CharField(model_attr='school')
    semester = IntegerField(model_attr='semester')
    academic_year = IntegerField(model_attr='academic_year')


class FileIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    school = CharField(model_attr='school')
    corse = CharField(model_attr='course')

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='title')

    # Use Apache Solr's Rich Content Extraction
    # To index document text for search
    def prepare(self, obj):
        data = super(FileIndex, self).prepare(obj)

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

        return data


site.register(File, FileIndex)
site.register(School, SchoolIndex)
site.register(Course, CourseIndex)
