from django import forms
from models import School, Course, Note, Tag


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="")
    school = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
    note_file  = forms.FileField(label='File')


class SelectTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
