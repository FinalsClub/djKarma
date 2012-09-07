"""
Index descriptions to make various models searchable.
"""
from haystack import indexes
from haystack.fields import EdgeNgramField
from models import School, Course, File


class SchoolIndex(indexes.SearchIndex, indexes.Indexable):
    # documenet=True indicates this is the primary search field

    # use_template allows us to specify a django-style template
    # containing all the relevant text for a School
    # without use_template=True Haystack concatenates all the fields
    # which apparently can be undesirable
    # See ./KNotes/templates/search/indexes/notes/school_text.txt
    text = indexes.CharField(document=True, use_template=True)

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='name')

    # Example custom queryset for objects to add to index
    # For Schools, we'll index the complete set
    '''
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Note.objects.filter(pub_date__lte=datetime.datetime.now())
    '''

    def get_model(self):
        return School


class CourseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='title')

    # Non document fields allow for search filtering
    # i.e: Search "math" at school Harvard
    school = indexes.CharField(model_attr='school')
    semester = indexes.IntegerField(model_attr='semester')
    academic_year = indexes.IntegerField(model_attr='academic_year')

    def get_model(self):
        return Course


class FileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    school = indexes.CharField(model_attr='school')
    corse = indexes.CharField(model_attr='course')

    # An EdgeNgramField for partial-match queries
    content_auto = EdgeNgramField(model_attr='title')

    def get_model(self):
        return File

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
            #extracted_data = self._get_backend(None).extract_file_contents(file_obj)
            # Now we'll finally perform the template processing to render the
            # text field with *all* of our metadata visible for templating:
            t = indexes.loader.select_template(('search/indexes/notes/file_text.txt', ))
            data['text'] = t.render(indexes.Context({'object': obj,
                                             'extracted': extracted_data}))
        except IOError:
            print "FileIndex: error accessing " + obj.file.path
            # actual file is not available

