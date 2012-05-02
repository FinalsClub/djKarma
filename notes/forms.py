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

import datetime
from django import forms
from models import School, Course, File, Tag, Instructor
from simple_autocomplete.widgets import AutoCompleteWidget
from simplemathcaptcha.fields import MathCaptchaField
from django.template.defaultfilters import slugify


# User Profile form
class ProfileForm(forms.Form):

    school = forms.ModelChoiceField(
        required=False,
        queryset=School.objects.all(),
        error_messages={'invalid_choice': 'Select a valid school.',
                        'required': 'Select a school.'},
        widget=forms.Select(attrs={'class': 'span2'})
    )
    grad_year = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'span2'}))

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Auto populate the graduation_year choiceField with
        # a 75 year range
        #birth_day = forms.ChoiceField(choices=((str(x), x) for x in range(1,32)))
        years = range(datetime.datetime.now().year - 30, datetime.datetime.now().year + 5)
        years.insert(0, '')
        year_tuples = ((str(x), x) for x in years)
        self.fields['grad_year'].choices = year_tuples


# Create school form
class SchoolForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})

    class Meta:
        model = School


# Create course form
class CourseForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        widget=AutoCompleteWidget(
            url='/instructors',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid instructor. Begin typing an instructor name to see available choices.',
                        'required': 'Enter an instructor.'},
    )

    class Meta:
        model = Course
        #fields = ('title', 'school')


# Create Instructor form
class InstructorForm(forms.ModelForm):
    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})

    class Meta:
        model = Instructor


# Upload file form
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
        error_messages={'invalid_choice': 'Enter a valid school. Begin typing a school name to see available choices.',
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
    '''
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        widget=AutoCompleteWidget(
            url='/instructors',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid instructor. Begin typing an instructor name to see available choices.',
                        'required': 'Enter an instructor.'},
    )
    '''
    # TODO: Try autocomplete widget for tags
    tags = forms.CharField(max_length=511, label="Tags (separated with commas)", error_messages={'required': 'Help us organize. Add some tags.'})
    '''
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'),
                                        error_messages={'required': 'Help us organize. Add some tags.'}, )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=AutoCompleteMultipleWidget(
            url='/tags',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid tag. Begin typing a tag name to see available choices.',
                        'required': 'Enter an instructor.'},
    )
    '''

    captcha = MathCaptchaField(required=True, error_messages={'required': 'Prove you\'re probably a human.'})
    agree = forms.BooleanField(required=True, label='I Agree to the Terms of Use',
                               error_messages={'required': 'We aren\'t evil, check out the Terms.'})
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )
    note_file = forms.FileField(label='File', error_messages={'required': 'Attach a file'})


# Form to search tags by selecting in multiple-choice select widget
class SelectTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.order_by('name'))


class CsvTagField(forms.CharField):
    # Convert text input to Array of Tag objects
    # For form TypeTagsForm.is_valid() to be true, let's make sure at least one
    # existing tag is entered
    def clean(self, value):
        values = value.split(',')
        result = []
        # Iterate through submitted tags
        for value in values:
            # If the tag is empty, ignore it
            if slugify(value) == "":
                continue
            try:
                # Return if tag matching query found
                result.append(Tag.objects.get(name=slugify(value)))
            except:
                pass
                # If the tag does not exist, move on
        if len(result) == 0:
            # If we don't recognize any of the tags, raise Error
            raise forms.ValidationError("Sorry, those tags aren't in our system... yet.")
        #print "field clean result: " + str(result)
        return result


# Form to search tags by typing csv separated tags
class TypeTagsForm(forms.Form):
    tags = CsvTagField(max_length=511, label="Tags (separated with commas)", error_messages={'required': 'Enter tags to search.'})
