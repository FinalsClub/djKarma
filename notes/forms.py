from django import forms
from models import School, Course, Note, Tag
#from autocomplete.widgets import AutocompleteSelectMultiple
from simple_autocomplete.widgets import AutoCompleteWidget


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    #course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="")
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=AutoCompleteWidget(
            url='/courses',
            initial_display=''
        )
    )
    #school = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        widget=AutoCompleteWidget(
            url='/schools',
            initial_display=''
        ),
        # TODO: Figure out how to override the default invalid message.
        error_messages={'invalid': 'Enter a valid course. Begin typing a course name to see available choices.'},
    )
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )
    note_file  = forms.FileField(label='File')


class SelectTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
