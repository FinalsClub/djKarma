# Copyright (C) 2012  FinalsClub Foundation
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from models import School, Course, Note, Tag
#from autocomplete.widgets import AutocompleteSelectMultiple
from simple_autocomplete.widgets import AutoCompleteWidget


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    #course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="")
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        initial=3,
        widget=AutoCompleteWidget(
            url='/courses',
            initial_display=''
        )
    )
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
