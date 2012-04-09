from django import forms
from models import School, Course, Note


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), 
    								empty_label="")
    school = forms.ModelChoiceField(queryset=School.objects.all(), 
    								empty_label="")
    note_file  = forms.FileField(label='File')