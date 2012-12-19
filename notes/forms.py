#!/usr/bin/python
# -*- coding:utf8 -*-
"""
"""
# Copyright (C) 2012  FinalsClub Foundation

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from simple_autocomplete.widgets import AutoCompleteWidget
from simplemathcaptcha.fields import MathCaptchaField

from models import School, Course, Note, Tag, Instructor


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='We\'ll send you a confirmation message. Your on-site avatar is linked to your email with <a href=\"http://www.gravatar.com\">Gravatar</a>')
 
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")
 
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class CaptchaForm(forms.Form):
    captcha     = MathCaptchaField(required=True, \
                    error_messages={'required': 'Prove you\'re probably a human.'})

class FileMetaDataForm(forms.Form):
    file_pk      = forms.CharField(max_length=255, \
                    widget=forms.HiddenInput(attrs={'id': 'file-form-file_pk'}))
    school_pk      = forms.CharField(max_length=255, \
                    widget=forms.HiddenInput(attrs={'id': 'file-form-school_pk'}))
    course_pk      = forms.CharField(max_length=255, \
                    widget=forms.HiddenInput(attrs={'id': 'file-form-course_pk'}))
    type        = forms.ChoiceField(choices=Note.FILE_PTS)
    title       = forms.CharField(max_length=50, \
                    error_messages={'required': 'Enter a title.'}, \
                    widget=forms.TextInput(attrs={'class': 'text-input'}))
    description = forms.CharField(required=False, max_length=511, \
                    error_messages={'required': 'Enter a description.'}, \
                    widget=forms.Textarea(attrs={'class': 'text-input'}))
    tags        = forms.CharField(required=False, max_length=511, \
                    label="Tags", \
                    error_messages={'required': 'Help us organize. Add some tags.'}, \
                    widget=forms.TextInput(attrs={'placeholder':'ex: math, uncertainty, statistics', 'class': 'text-input'}))
    captcha     = MathCaptchaField(required=True, \
                    error_messages={'required': 'Prove you\'re probably a human.'})
    in_course = forms.BooleanField(required=False, label='I\'m currently in this course')
    # only show this for new users, or the first time a user uploads. We should stores this on the userprofile
    # That would require us to create a special user type, called the Zero User 
    agree       = forms.BooleanField(required=True, \
                    label='I Agree to the Terms of Use',
                    error_messages={'required': 'We aren\'t evil, check out the Terms.'})

    required_css_class = 'required'

class FileMetaDataFormNoCaptcha(forms.Form):
    file_pk     = forms.CharField(\
                    max_length=255,
                    widget=forms.HiddenInput(
                        attrs={'id': 'file-form-file_pk'}
                    )
                )
    school_pk   = forms.CharField(max_length=255, \
                    widget=forms.HiddenInput(
                        attrs={'id': 'file-form-school_pk'}
                    )
                )
    course_pk   = forms.CharField(max_length=255,
                    widget=forms.HiddenInput(
                        attrs={'id': 'file-form-course_pk'}
                    )
                )
    type        = forms.ChoiceField(choices=Note.FILE_PTS, required=False)
    created_on        = forms.DateField(required=False)
    title       = forms.CharField(max_length=50,
                    error_messages={'required': 'Enter a title.'},
                    widget=forms.TextInput(attrs={'class': 'text-input'})
                )
    description = forms.CharField(required=False, max_length=511,
                    error_messages={'required': 'Enter a description.'},
                    widget=forms.Textarea(attrs={'class': 'text-input'})
                )


    #tags        = forms.CharField(required=False, max_length=511, \
    #                label="Tags", \
    #                error_messages={'required': 'Help us organize. Add some tags.'}, \
    #                widget=forms.TextInput(attrs={'placeholder':'ex: math, uncertainty, statistics', 'class': 'text-input'}))
    #captcha     = MathCaptchaField(required=True, \
    #                error_messages={'required': 'Prove you\'re probably a human.'})
    in_course = forms.BooleanField(required=False, label='I\'m currently in this course')
    # only show this for new users, or the first time a user uploads. We should stores this on the userprofile
    # That would require us to create a special user type, called the Zero User 
    #agree       = forms.BooleanField(required=True, \
    #                label='I Agree to the Terms of Use',
    #                error_messages={'required': 'We aren\'t evil, check out the Terms.'})

    required_css_class = 'required'

    #school     = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )

class FileUploadForm(forms.Form):
    file = forms.FileField(required=True, label='File', error_messages={'required': 'Attach a file'})

    required_css_class = 'required'

##########################
### Upload Usher Forms ###
##########################


class CharInstructorField(forms.CharField):
    """ Convert text instructor name to Instructor model
        creating one if necessary
    """
    def clean(self, value):
        if Instructor.objects.filter(name=value).exists():
            instructor = Instructor.objects.get(name=value)
        else:
            instructor = Instructor.objects.create(name=value)
        return instructor


class CharSchoolField(forms.CharField):
    """ Convert text school name to School model
        creating one if necessary
    """
    def clean(self, value):
        if School.objects.filter(pk=value).exists():
            school = School.objects.get(pk=value)
        else:
            # This should never happen as this field is hidden
            # and populated by javascript in uploadUsher.html
            raise forms.ValidationError("Sorry, the seleted School does not exist.")
        return school


class CharCourseField(forms.CharField):
    """ Convert text school name to School model
        creating one if necessary
    """
    def clean(self, value):
        if Course.objects.filter(pk=value).exists():
            course = Course.objects.get(pk=value)
        else:
            # This should never happen as this field is hidden
            # and populated by javascript in uploadUsher.html
            raise forms.ValidationError("Sorry, the seleted Course does not exist.")
        return course


# CreateCourseForm is not currently used. Just used it to autorender the needed html
class CreateCourseForm(forms.ModelForm):
    """ Form used when creating a new course
    """
    class Meta:
        model = Course
        fields = ('title', 'field', 'instructor_email', 'instructor_name', 'desc')

class GenericCharForm(forms.Form):
    """ Provides a means to sanitize generic text received via GET/POST """
    text = forms.CharField(max_length=255)

class ModelSearchForm(forms.Form):
    """ Provides the form of the Search field """
    title = forms.CharField(max_length=127, widget=forms.TextInput(attrs={'class':'text-input'}))


class UsherUploadFileForm(forms.Form):
    type        = forms.ChoiceField(choices=Note.FILE_PTS)
    title       = forms.CharField(max_length=50, \
                    error_messages={'required': 'Enter a title.'})
    description = forms.CharField(required=False, max_length=511, \
                    error_messages={'required': 'Enter a description.'})
    school      = CharSchoolField(max_length=255, \
                    widget=forms.HiddenInput(attrs={'id': 'usherUpload-school'}))
    course      = CharCourseField(max_length=255, \
                    widget=forms.HiddenInput(attrs={'id': 'usherUpload-course'}))
    tags        = forms.CharField(required=False, max_length=511, \
                    label="Tags (separated with commas)", \
                    error_messages={'required': 'Help us organize. Add some tags.'})
    captcha     = MathCaptchaField(required=True, \
                    error_messages={'required': 'Prove you\'re probably a human.'})
    agree       = forms.BooleanField(required=True, \
                    label='I Agree to the Terms of Use',
                    error_messages={'required': 'We aren\'t evil, check out the Terms.'})
    note_file   = forms.FileField(label='File', error_messages={'required': 'Attach a file'})

    required_css_class = 'required'

    #school     = forms.ModelChoiceField(queryset=School.objects.all(), empty_label="")
    #tags = forms.ModelMultipleChoiceField(Tag, widget=AutocompleteSelectMultiple(Tag, search_fields=['name']), )



class UsherCourseForm(forms.ModelForm):
    """ Create course form with hidden school field
        school is populated with javascript based on the previous School selection
    """
    #captcha     = MathCaptchaField(required=True, \
    #                error_messages={'required': 'Prove you\'re probably a human.'})
    instructor  = CharInstructorField(required=False, \
                    max_length=127, \
                    error_messages={'required': 'Please Enter your Instructor\'s Name'})
    # school is populated with the school Model pk with javascript.See uploadUsher.html
    school      = CharSchoolField(max_length=255, widget=forms.HiddenInput())

    class Meta:
        model = Course
        #fields = ('title', 'school')


    def clean(self):
        """ Convert school and instructor CharFields to Models, then validate
            Instructor.school = school
        """
        # TODO: Refactor model does not exist errors to field clean() methods
        cleaned_data = super(UsherCourseForm, self).clean()

        # Verify Instructor belongs to given school
        if cleaned_data.get("instructor") != None and cleaned_data.get("instructor").school != None:
            if cleaned_data.get("instructor").school != cleaned_data.get("school"):
                error_string = "Selected Professor belongs to %s" % (cleaned_data.get("instructor").school.name)
                raise forms.ValidationError(error_string)

        return cleaned_data

##########################
###  End Upload Usher  ###
##########################


class ProfileForm(forms.Form):
    """ User Profile form for inline profile editing
        Used in profile.html
    """

    school      = forms.ModelChoiceField(
                    required=False,
                    queryset=School.objects.all(),
                    error_messages={'invalid_choice': 'Select a valid school.',
                                    'required': 'Select a school.'},
                    widget=forms.Select(attrs={'class': 'profile-field-school'})
                )
    grad_year   = forms.ChoiceField(
                    required=False,
                    widget=forms.Select(attrs={'class': 'profile-field-year'})
                )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Auto populate the graduation_year choiceField with
        # a 75 year range
        #birth_day = forms.ChoiceField(choices=((str(x), x) for x in range(1,32)))
        years = range(1980, 2016) # TODO: update this value once a year
        years.insert(0, '')
        year_tuples = ((str(x), x) for x in years)
        self.fields['grad_year'].choices = year_tuples


class SchoolForm(forms.ModelForm):
    """ Create school form """
    captcha = MathCaptchaField(required=True, \
                error_messages={'required': 'Prove you\'re probably a human.'})

    class Meta:
        model = School


# Create course form
# DEPRECATED. To be removed after UploadUsher is functional
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

class SmartSchoolForm(forms.Form):
    """ Making a autocomplete field for just school as part of the upload process
    """
    # FIXME: terrible name
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        widget=AutoCompleteWidget(
            url='/schools',
            initial_display=''
        ),
        error_messages={'invalid_choice': 'Enter a valid school. Begin typing a school name to see available choices.',
                        'required': 'Enter a school.'},
    )

# Upload file form
class UploadFileForm(forms.Form):
    type = forms.ChoiceField(choices=Note.FILE_PTS)
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
