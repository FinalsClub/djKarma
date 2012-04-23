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
from models import School, Course, File, Tag, Instructor
from simple_autocomplete.widgets import AutoCompleteWidget, AutoCompleteMultipleWidget
from simplemathcaptcha.fields import MathCaptchaField


class SchoolForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    class Meta:
        model = School


class CourseForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    class Meta:
        model = Course
        #fields = ('title', 'school')


class InstructorForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    class Meta:
        model = Instructor


class UploadFileForm(forms.Form):
    type = forms.ChoiceField(choices=File.FILE_PTS)
    title = forms.CharField(max_length=50, error_messages={'required': 'Enter a title.'})
    description = forms.CharField(max_length=511, error_messages={'required': 'Enter a description.'})
    #school = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        widget=AutoCompleteWidget(
            url='/schools',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid school. Begin typing a course name to see available choices.',
                        'required': 'Enter a school.'},
    )
    #course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="")
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=AutoCompleteWidget(
            url='/courses',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid course. Begin typing a course name to see available choices.',
                        'required': 'Enter a course.'},
    )
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        widget=AutoCompleteWidget(
            url='/instructors',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid instructor. Begin typing a course name to see available choices.',
                        'required': 'Enter an instructor.'},
    )
    # TODO: Try autocomplete widget for tags
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'),
                                        error_messages={'required': 'Help us organize. Add some tags.'}, )
    '''
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=AutoCompleteMultipleWidget(
            url='/tags',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid instructor. Begin typing a course name to see available choices.',
                        'required': 'Enter an instructor.'},
    )
    '''

    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    agree = forms.BooleanField(required=True, label='I Agree to the Terms of Use',
                               error_messages={'required': 'We aren\'t evil, check out the Terms.'})
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )
    note_file = forms.FileField(label='File', error_messages={'required': 'Attach a file'})


class SelectTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))
