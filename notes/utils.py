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



def nav_helper(request, response={}):
    """ calculates information for the navigation sidebar for logged in users
        :request:  a Request object that contains a user &etc
        :response: (optional) a response dictionary to pass to the template
        returns: a response dictionary
    """
    # TODO: turn this into a middleware or decorator
    # TODO: implement the zero-user-model

    # Calculate User's progress towards next Karma level
    # Depends on models.Level objects
    user_profile = request.user.get_profile()

    user_level = request.user.get_profile().getLevel()
    response['current_level'] = user_level['current_level']
    if user_profile.school != None:
        response['school_pk'] = user_profile.school.pk
    else:
        response['school_pk'] = 0

    # The user has reached the top level
    if not 'next_level' in user_level:
        #print user_level['current_level'].title + " Top Level"
        response['progress'] = 100
    else:
        #print user_level['current_level'].title + " " + user_level['next_level'].title
        response['next_level'] = user_level['next_level']
        response['progress'] = (user_profile.karma / float(response['next_level'].karma)) * 100

    #Pre-populate ProfileForm with user's data

        # If user has a school selected, fetch recent additions to School
        # For the user's news feed
        #response['recent_files'] = Note.objects.filter(school=request.user.get_profile().school).order_by('-timestamp')[:5]

    response['messages'] = complete_profile_prompt(user_profile)
    response['share_url'] = u"http://karmanotes.org/sign-up/{0}".format(user_profile.get_name())
    response['user_profile'] = user_profile
    response = get_upload_form(response)

    # Check for uploads made during this django session
    # while user was not authenticated
    _post_user_create_session_hook(request)

    # home built auto-complete
    '''
    if not user_profile.school:
        response['available_schools'] = [(str(school.name), school.pk) for school in School.objects.all().order_by('name')]
    if not user_profile.grad_year:
        response['available_years'] = range(datetime.datetime.now().year, datetime.datetime.now().year + 10)
    '''
    response['available_schools'] = [(unicode(school.name), school.pk) for school in School.objects.all().order_by('name')]
    response['available_years'] = range(datetime.datetime.now().year, datetime.datetime.now().year + 10)

    return response


def get_upload_form(response):
    """ Appends forms required for upload form to response
        The way to make this smooth is:
            user types option in autocomplete field >
            after 3 characters, we search that via ajax
            user is presented with options
            when user clicks one of the options or hits enter, submits and saves school on field
            the submit button also triggers the course field to appear like the school
            when course is selected / created submits and saves course to file
            course submit makes the metadata section appear
    """
    response['school_form'] = SmartSchoolForm
    return response


def jsonifyModel(model, depth=0, user_pk=-1):
    """ Returns a python dictionary representation of a model
        The resulting model is ready for json.dumps()
        model is a Django Model

        optional: depth is how many levels of foreignKey introspection should be performed
            jsonifyModel(model=School, depth=1) returns school json at course detail
            jsonifyModel(model=School, depth=2) returns school json at note detail
        optional: user_pk for inclusion of moderation data in file response

        i.e: has the user voted on this file?
    """
    json_result = {}
    if isinstance(model, School):
        json_result["_id"] = model.pk
        json_result["name"] = model.name
        json_result["location"] = model.location
        json_result["courses"] = []
        if(depth > 0):
            for course in model.course_set.all().order_by('title'):
                course_json = jsonifyModel(model=course, depth=depth - 1, user_pk=user_pk)
                json_result["courses"].append(course_json)
    elif isinstance(model, Course):
        json_result["_id"] = model.pk
        json_result["title"] = model.title
        json_result["instructor"] = model.instructor.name
        json_result["notes"] = []
        json_result["num_notes"] = len(model.files.all())
        if(depth > 0):
            for note in model.files.all().order_by('-timestamp'):
                note_json = jsonifyModel(model=note, user_pk=user_pk)
                json_result["notes"].append(note_json)
    elif isinstance(model, Note):
        json_result["_id"] = model.pk
        json_result["notedesc"] = model.title
        json_result["views"] = model.viewCount
        json_result["pts"] = model.numUpVotes - model.numDownVotes
        json_result["upvotes"] = model.numUpVotes

        # If the file has an owner, provide it
        if model.owner != None:
            json_result["user"] = model.owner.get_profile().get_name()
        else:
            json_result["user"] = "KN Staff"

        # If a valid user_pk is provided, and that user has voted on this file add vote data
        # If a valid user_pk is provided, and that user matches the file owner, indicate that
        # For performance, validate user_pk before calling jsonifyModel
        # now only check that user_pk != -1
        # Before: 2.42 s
        # After: 2.11 s
        if int(user_pk) != -1:
            print user_pk
            request_user = User.objects.get(pk=user_pk)
            # If the valid user has voted on this file, bundle vote value:
            if model.votes.filter(user=request_user).exists():
                #print "*** user voted"
                # user has all ready voted
                json_result["canvote"] = 1
                user_file_vote = model.votes.get(user=request_user).up
                if user_file_vote == True:
                    json_result["vote"] = 1  # upvote
                elif user_file_vote == False:
                    json_result["vote"] = -1  # downvote
            else:
                # The valid user has not voted on this file
                json_result["vote"] = 0  # novote
                # If the valid user owns the file, don't allow voting
                if model.owner != None and model.owner == request_user:
                    json_result["owns"] = 1
                    #print "*** user owns file"
                    json_result["canvote"] = 0
                    json_result["vote"] = 1
                # Else If the valid user has viewd the file, allow voting
                elif request_user.get_profile().files.filter(pk=model.pk).exists():
                    #print "*** user has viewed file!"
                    json_result["canvote"] = 1
                    json_result["owns"] = 0
                # Else the valid user does not own, and has not viewed, so don't allow voting
                else:
                    #print "*** no user connection"
                    json_result["canvote"] = 0
                    json_result["owns"] = 0
        else:
            #print "*** user dne"
            # A valid user_pk was not provided
            json_result["canvote"] = 0
            json_result["vote"] = 0  # novote

    return json_result


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
    if file.owner == user or user.get_profile().files.filter(pk=file.pk).exists():
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

