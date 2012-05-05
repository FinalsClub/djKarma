from haystack.indexes import *
from haystack import site
from models import School, Course


class SchoolIndex(SearchIndex):
    # documenet=True indicates this is the primary search field

    # use_template allows us to specify a django-style template
    # containing all the relevant text for a School
    # without use_template=True Haystack concatenates all the fields
    # which apparently can be undesirable
    # See ./KNotes/templates/search/indexes/notes/school_text.txt
    text = CharField(document=True, use_template=True)

    # Example custom queryset for objects to add to index
    # For Schools, we'll index the complete set
    '''
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Note.objects.filter(pub_date__lte=datetime.datetime.now())
    '''


class CourseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    # Non document fields allow for search filtering
    # i.e: Search "math" at school Harvard
    school = CharField(model_attr='school')
    semester = IntegerField(model_attr='semester')
    academic_year = IntegerField(model_attr='academic_year')


site.register(School, SchoolIndex)
site.register(Course, CourseIndex)
