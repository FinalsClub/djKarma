# Copyright (C) 2012  FinalsClub Foundation

import datetime

from django import forms as djangoforms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from forms import SmartSchoolForm
from forms import UploadFileForm
from simple_autocomplete.widgets import AutoCompleteWidget

from KNotes import settings
from models import School, Course, Note, Tag, UserProfile
from notes import profile_tasks

def _post_user_create_session_hook(request):
    """ 
        After a user logs in for the first time, their landing page needs to be
        hooked into this function. This takes any files they may have uploaded
        as an anon user and saves them to the new user object.
        This might make more sense as a middleware, but this works for now.
    """
    print 'post_user_create hook!'
    if settings.SESSION_UNCLAIMED_FILES_KEY in request.session:
        print 'found unclaimed files session key'
        for unclaimed_file_pk in request.session[settings.SESSION_UNCLAIMED_FILES_KEY]:
            try:
                unclaimed_file = Note.objects.get(pk=unclaimed_file_pk)
                unclaimed_file.owner = request.user
                unclaimed_file.save()  # Handles generating Event + Awarding Karma
                print "saved " + str(unclaimed_file.title)
            except:
                print "We couldn't save this user's files"
        del request.session[settings.SESSION_UNCLAIMED_FILES_KEY]


def processCsvTags(file, csvString):
    """ Retrieve or Create a tag corresponding to each string
        and assign it to file
            file: a Note object
            csvString: a csv string of Tags
    """
    if not isinstance(file, Note):
        return False
    tagStrs = csvString.split(',')
    for tagStr in tagStrs:
        # If the tag is empty, ignore it
        if slugify(tagStr) == "":
            continue
        #print tagStr + " : " + str(slugify(tagStr))
        tag, created = Tag.objects.get_or_create(name=slugify(tagStr))
        #print "tag created: " + str(created)
        #print "tag name: " + tag.name
        file.tags.add(tag)
    return True


def uploadForm(user):
    """ Creates an UploadFileForm and pre-populates the school field
        With the user's school, if available
        is currently unused?
    """
    #print request.user.username
    user_profile = user.get_profile()
    if user_profile.school:
        print "The user has a school, so we will auto populate it"
        # This isn't the ideal way to override the field system. I would rather extend or replicate the existing UploadFileForm, but I am slightly unsure how to do that
        # Alternatively, I could figure out how to use the 'school' kv argument
        form = UploadFileForm(initial={'course': -1, 'school': user_profile.school.pk})
        form.fields['school'] = djangoforms.ModelChoiceField(
                queryset=School.objects.all(),
                widget=AutoCompleteWidget(
                    url='/schools',
                    initial_display=user_profile.school.name
                ),
                error_messages={'invalid_choice': 'Enter a valid school. Begin typing a school name to see available choices.',
                                'required': 'Enter a school.'},
            )
    else:
        # Provide bogus default school and course data to ensure
        # legitimate data is chosen
        form = UploadFileForm(initial={'course': -1, 'school': -1})
    return form


def complete_profile_prompt(user_profile):
    """ Creates a list of prompts for the user to do to complete their profile
        Takes a User object
        Returns a list of template strings
    """
    profile_todo = []
    for task in profile_tasks.tasks:
        if not task.check(task(), user_profile):
            # for tasks that are not done, add them to todo list
            profile_todo.append(task)
    # return list of message prompts for the user to be told on the profile page
    messages = [{"body": task.message, "div_id": task.div_id} for task in profile_todo]
    return messages


def userCanView(user, file):
    """ :user: django user
        :file: a notes.models.Note object
        returns True/False
    """
    if file.owner == user or user.get_profile().viewed_notes.filter(pk=file.pk).exists():
        print "user can view!"
        return True
    return False


class Janitor():
    """ Collection of cleanup functions for the notes app """

    @staticmethod
    def create_model_slugs(Model):
        """ Create slug fields for models that do not currently have them
            model: a model with a name **or** title field, but not both, and a slug field
            returns t/f, success string
        """
        slugs_created = 0
        for i in Model.objects.filter(slug__isnull=True).all():
            if hasattr(i, 'name'):
                i.slug = slugify(i.name)
            elif hasattr(i, 'title'):
                i.slug = slugify(i.title)
            else:
                return False, u"The model you passed to create slugs, does not have a name or title field"
            i.save()
            slugs_created += 1
        return True, u"Created %s slugs on: %s" % (slugs_created, Model)

    @staticmethod
    def generate_gravatar_urls():
        """ Re-generates self.picture_url_small and self.picture_url_large
            for all users. Run this after changing default image urls in
            UserProfile.get_picture
        """
        users = UserProfile.objects.all()
        for user in users:
            if user.user.email != None:
                user.picture_url_large = user.get_picture('large')
                user.picture_url_small = user.get_picture('small')
                user.save

