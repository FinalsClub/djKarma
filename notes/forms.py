from django import forms
from models import School, Course, Note, Tag
#from autocomplete.widgets import AutocompleteSelectMultiple
from simple_autocomplete.widgets import AutoCompleteWidget


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="")
    #school = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        initial=3,
        widget=AutoCompleteWidget(
            url='/schools',
            initial_display=''
        )
    )
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )
    note_file  = forms.FileField(label='File')


class SelectTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
