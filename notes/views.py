# Copyright (C) 2012  FinalsClub Foundation

import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.encoding import iri_to_uri
from ajaxuploader.views import AjaxFileUploader

from forms import UploadFileForm
from forms import UsherCourseForm
from forms import ModelSearchForm
from forms import TypeTagsForm
from forms import SchoolForm
from forms import InstructorForm
from forms import ProfileForm
from forms import FileMetaDataForm
from forms import SmartSchoolForm
from models import School
from models import Course
from models import File
from models import Instructor
from models import SiteStats
from models import Level
from models import Vote
from models import ReputationEventType
from utils import complete_profile_prompt
from utils import jsonifyModel
from utils import processCsvTags
from utils import userCanView

import datetime

#from django.core import serializers

## :|: Static pages :|: &
def home(request):
    """ Landing Page [static] """
    # Get the 'singleton' SiteStats instance
    stats = SiteStats.objects.get(pk=1)

    #Get recently uploaded files
    recent_files = File.objects.order_by('-timestamp')[:7]
    print recent_files

    return render(request, 'home.html', {'stats': stats, 'recent_files': recent_files})

def about(request):
    return render(request, 'static/about.html')

def terms(request):
    return render(request, 'static/ToS.html')

## :|: Uploading :|: &

# For Ajax Uploader
import_uploader = AjaxFileUploader()


# One-shot file uploader with async Google processing
def modalUpload(request):
    template_data = {}
    template_data['search_form'] = ModelSearchForm
    template_data['file_form'] = FileMetaDataForm
    return render(request, 'modalUpload.html', template_data)


# Handles file meta data submission separate from file upload
def fileMeta(request):
    if request.method == "POST" and request.is_ajax():
        response = {}
        form = FileMetaDataForm(request.POST)
        if form.is_valid():
            file = File.objects.get(pk=form.cleaned_data["file_pk"])
            file.type = form.cleaned_data["type"]
            file.title = form.cleaned_data["title"]
            file.descriptioin = form.cleaned_data["description"]
            # process Tags
            processCsvTags(file, form.cleaned_data['tags'])
            file.save()
            response = {}
            response["status"] = "success"
            response["file_pk"] = file.pk
            if request.user.is_authenticated():
                # This should let us use django's messaging system to do the alert-notifications
                # in our design on upload success at the top of the profile
                # FIXME: fix this message with proper html
                messages.add_message(request, messages.SUCCESS, "Success! You uploaded a file (message brought to you by Django Messaging!")
        else:
            response["form"] = form
            response["message"] = "Please check your form data."
            return TemplateResponse(request, 'ajaxFormResponse_min.html', response)
    else:
        response["status"] = "invalid request"
    return HttpResponse(json.dumps(response), mimetype="application/json")


def smartModelQuery(request):
    """ Accessed by charfields corresponding to a model title/name
        See if model with similiar title exists and return title
        If not, return model create form with populated title/name
    """
    if request.method == 'POST' and request.is_ajax():
        search_form = ModelSearchForm(request.POST)
        if search_form.is_valid():
            if request.POST['type'] == "School":
                # If no school matching text entry exists, present School Form
                if not School.objects.filter(name=search_form.cleaned_data['title']).exists():
                    form = SchoolForm(initial={'name': search_form.cleaned_data['title']})
                    message = "Tell us a little more about your school"
                    # Return a list of all schools to present to user, ensuring duplicate entires aren't made
                    # TODO: Try searching school name with input, return mathing results
                    schools = School.objects.all().values('name', 'pk').order_by('name')
                    print "smartModelQuery: return create School ajaxFormResponse"
                    return TemplateResponse(request, 'ajaxFormResponse.html', {'form': form, 'type': request.POST['type'], 'message': message, 'suggestions': schools})
                # A school matching entry exists
                else:
                    # Return a json object: {'status': 'success', 'model': model's pk}
                    response = {}
                    response['status'] = 'success'
                    response['type'] = 'school'
                    response_school = School.objects.get(name=search_form.cleaned_data['title'])
                    response['model_pk'] = response_school.pk
                    response['model_name'] = response_school.name
                    return HttpResponse(json.dumps(response), mimetype="application/json")
            if request.POST['type'] == "Course":
                # If no course matching text entry exists, present Course Form
                if not Course.objects.filter(title=search_form.cleaned_data['title']).exists():
                    form = UsherCourseForm(initial={'title': search_form.cleaned_data['title']})
                    message = "Tell us a little more about your course"
                    courses = None
                    if request.GET.get("school", -1) != -1:
                        courses = Course.objects.filter(school=School.objects.get(pk=request.GET.get("school"))).values("title", "pk").order_by('title')
                    print "smartModelQuery: return create Course ajaxFormResponse"
                    return TemplateResponse(request, 'ajaxFormResponse.html', {'form': form, 'type': request.POST['type'], 'message': message, 'suggestions': courses})
                # A course matching entry exists
                else:
                    # Return a json object: {'status': 'success', 'model': 'model's pk, 'model_title': title}
                    response = {}
                    response['status'] = 'success'
                    response['type'] = 'course'
                    response_course = Course.objects.get(title=search_form.cleaned_data['title'])
                    response['model_pk'] = response_course.pk
                    response['model_name'] = response_course.title
                    return HttpResponse(json.dumps(response), mimetype="application/json")
    raise Http404

@login_required
def profile(request):
    """ User Profile """
    response = {}

    # Calculate User's progress towards next Karma level
    # Depends on models.Level objects
    user_profile = request.user.get_profile()

    user_level = request.user.get_profile().getLevel()
    response['current_level'] = user_level['current_level']

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
        #response['recent_files'] = File.objects.filter(school=request.user.get_profile().school).order_by('-timestamp')[:5]

    response['messages'] = complete_profile_prompt(user_profile)
    response['share_url'] = u"http://karmanotes.org/sign-up/{0}".format(user_profile.hash)
    response['user_profile'] = user_profile
    response = get_upload_form(response)

    # home built auto-complete
    if not user_profile.school:
        response['available_schools'] = [(str(school.name), school.pk) for school in School.objects.all().order_by('name')]
    if not user_profile.grad_year:
        response['available_years'] = range(datetime.datetime.now().year, datetime.datetime.now().year + 10)
    response['course_json_url'] = '/jq_course' # FIXME: replace this with a reverse urls.py query
    return render(request, 'profile.html', response)


def editProfile(request):
    if(request.is_ajax()):
        response = {}
        do_save = False
        user_pk = int(request.GET.get('user', -1))
        print user_pk
        if user_pk == -1:
            raise Http404
        user_profile = User.objects.get(pk=user_pk).get_profile()
        if 'school' in request.GET:
            do_save = True
            user_profile.school = School.objects.get(pk=int(request.GET['school']))
            response['school'] = user_profile.school.name
            # When the user_profile is saved, submitted_school / year are adjusted
            if not user_profile.submitted_school:
                response['karma'] = ReputationEventType.objects.get(title="profile-school").actor_karma
        if 'year' in request.GET:
            do_save = True
            user_profile.grad_year = request.GET['year']
            response['year'] = user_profile.grad_year
            if not user_profile.submitted_grad_year:
                response['karma'] = ReputationEventType.objects.get(title="profile-grad-year").actor_karma

        if 'alias' in request.GET:
            do_save = True
            print "PRE: " + str(user_profile.alias)
            user_profile.alias = request.GET['alias']
            print "POST: " + str(user_profile.alias)
            response['alias'] = user_profile.alias

        if do_save:
            user_profile.save()
            response['status'] = 'success'
            return HttpResponse(json.dumps(response), mimetype="application/json")
        else:
            return HttpResponse(json.dumps({"status": "no input"}), mimetype="application/json")
    else:
        raise Http404

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


def addCourseOrSchool(request):
    """ handles user creation (via HTML forms) of auxillary objects:
        School, Course, and Instructor. Called by /upload
        UPDATED: Now also handles ajax requests from combined form page
        i.e: If ajax, just return updated form, not entire html page
    """
    if request.method == 'POST':
        if request.is_ajax():
            print "ajax request"
        else:
            print "non-ajax request"
        type = request.POST['type']
        if type == "Course":
            form = UsherCourseForm(request.POST)
        elif type == "School":
            form = SchoolForm(request.POST)
        elif type == "Instructor":
            form = InstructorForm(request.POST)
        if form.is_valid():
            model = form.save()

            #print "type: " + str(type).lower() + " model: " + str(model)
            # Trying to format the model properly for display in modelchoicefield
            #form = UploadFileForm(initial={str(type).lower(): [model.pk, str(model)]})

            # If ajax request, return success message
            if request.is_ajax():
                # Return a json object: {'status': 'success', 'model': 'model's pk}
                response = {}
                response['status'] = 'success'
                response['model_pk'] = model.pk

                if type == "Course":
                    response['model_name'] = model.title
                elif type == "School":
                    response['model_name'] = model.name

                return HttpResponse(json.dumps(response), mimetype="application/json")
            else:
                # Return to /upload page after object added
                # TODO: Have form reflect pre-populated value
                # With below line uncommented, the value is set to the form
                # But the autocomplete field does not reflect this in its display
                form = UploadFileForm(initial={str(type).lower(): model})
                return render(request, 'upload.html', {'message': str(type) + ' successfully created!', 'form': form})
        else:
            # If ajax, return only the form with errors
            if request.is_ajax():
                #return HttpResponse(form.errors)
                return TemplateResponse(request, 'ajaxFormResponse.html', {'form': form, 'type': type})
                #return render(request, 'ajaxFormResponse.html', {'form': form})
            # If not ajax, render entire form page
            else:
                return render(request, 'addCourseOrSchool.html', {'form': form, 'type': type})
    else:
        type = request.GET.get('type')
        if type == "Course":
            form = UsherCourseForm()
        elif type == "School":
            form = SchoolForm()
        elif type == "Instructor":
            form = InstructorForm()
        else:
            raise Http404
        return render(request, 'addCourseOrSchool.html', {'form': form, 'type': type})

def register(request, invite_code):
    """ Display user login and signup screens
        the registration/login.html template redirects login attempts
        to django's built-in login view (django.contrib.auth.views.login).
        new user registration is handled by this view (because there is no built-in)
    """
    if request.method == 'POST':
        #Fill form with POSTed data
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            print 'form valid'
            #Save the new user from form data
            new_user = form.save()
            #Authenticate the new user
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            #Login in the new user
            login(request, new_user)
            return HttpResponseRedirect("/profile")
        else:
            return render(request, "registration/register.html", {
        'form': form})
    else:
        form = forms.UserCreationForm()
        return render(request, "registration/register.html", {'form': form})


def instructors(request):
    """ Ajax: Instructor autcomplete form field """
    if request.is_ajax():
        query = request.GET.get('q')
        instructors = Instructor.objects.filter(name__contains=query).distinct()
        response = []
        for instructor in instructors:
            response.append((instructor.pk, instructor.name))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404


def schools(request):
    """ Ajax: School autcomplete form field """
    if request.is_ajax():
        query = request.GET.get('q')
        schools = School.objects.filter(name__icontains=query).distinct()
        response = []
        for school in schools:
            response.append((school.pk, school.name))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404

def jqueryui_courses(request):
    """ Ajax: Course autocomplete for jqueryui.autocomplete """
    # TODO: add optional filter by school and the javascript to support it
    query = request.GET.get('term')
    print "query %s" % query
    courses = Course.objects.filter(title__icontains=query).distinct()
    print "courses %s %s" % (len(courses), courses)
    response =  [(course.id, course.title) for course in courses]
    print json.dumps(response)
    return HttpResponse(json.dumps(response), mimetype="application/json")

def courses(request):
    """ Ajax: Course autocomplete form field """
    if True:
        query = request.GET.get('q')
        school_pk = request.GET.get('school', 0)
        # If no school provided, search all courses
        if school_pk == 0:
            courses = Course.objects.filter(title__icontains=query).distinct()
        # IF school provided, restrict search
        else:
            courses = Course.objects.filter(title__icontains=query, school=School.objects.get(pk=school_pk)).distinct()
        response = []
        for course in courses:
            response.append((course.pk, course.title))
        print response
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404


def browse(request):
    """ Browse and Search Notes """
    # If the SelectTagsForm form has been submitted, display search result
    if request.method == 'POST':
        # Use SelectTagsForm for a SelectMultiple Widget
        #tag_form = SelectTagsForm(request.POST)
        tag_form = TypeTagsForm(request.POST)
        if tag_form.is_valid():
            tags = tag_form.cleaned_data['tags']
            print "tags! " + str(tags)
            files = File.objects.filter(tags__in=tags).distinct()
            return render(request, 'notes2.html', {'files': files})
        else:
            return render(request, 'search.html', {'tag_form': tag_form})

    # If this is a GET request, display the SelectTagsForm
    else:
        # Use SelectTagsForm for a SelectMultiple Widget
        #tag_form = SelectTagsForm()
        tag_form = TypeTagsForm()
        return render(request, 'search.html', {'tag_form': tag_form})


@login_required
def note(request, note_pk):
    """ View Note HTML """
    # Check that user has permission to read
    profile = request.user.get_profile()
    # If the user does not have read permission, and the
    # Requested files is not theirs
    if not profile.can_read and not userCanView(request.user, File.objects.get(pk=note_pk)):
        user_karma = request.user.get_profile().karma
        level = Level.objects.get(title='Prospect')
        print level.karma
        progress = (user_karma / float(level.karma)) * 100
        return render(request, 'karma_wall.html', {'required_level': level, 'progress': progress, 'permission': 'access files'})
    try:
        note = File.objects.get(pk=note_pk)
    except:
        raise Http404
    # Increment note view count
    note.viewCount += 1
    note.save()

    # If this file is not in the user's collection, karmic purchase occurs
    if(not userCanView(request.user, File.objects.get(pk=note_pk))):
        # Buy Note viewing privelege for karma
        # awardKarma will handle deducting appropriate karma
        profile.awardKarma('view-file')
        # Add 'purchased' file to user's collection
        profile.files.add(note)
        profile.save()

    # This is ugly, but is needed to be able to get the note type full name
    note_type = [t[1] for t in note.FILE_TYPES if t[0] == note.type][0]
    url = iri_to_uri(note.file.url)
    return render(request, 'note.html', {'note': note, 'note_type': note_type, 'url': url})


def searchBySchool(request):
    """ Ajax: Return all schools and courses in JSON
        Used by search page javascript
    """
    response_json = []

    if request.is_ajax():
        schools = School.objects.all()
        for school in schools:
            school_json = jsonifyModel(model=school, depth=1)
            response_json.append(school_json)
        #print 'searchBySchool: ' + str(response_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")
    else:
        raise Http404

        #A nicer way to do this would be to override the queryset serializer
        #data = serializers.serialize("json", School.objects.all())
        #return HttpResponse(data, mimetype='application/json')
        #json_serializer = serializers.get_serializer("json")()
        #json_serializer.serialize(queryset, ensure_ascii=False, stream=response)


def notesOfCourse(request, course_pk):
    """ Ajax: Return all notes belonging to a course
        Used by search page javascript
    """
    # If user id is sent with search, send moderation data per note
    # i.e: has a user voted on this note?
    if request.is_ajax():
        user_pk = request.GET.get('user', '-1')
        # Validate request parameters
        if not Course.objects.filter(pk=course_pk).exists():
            raise Http404
        response_json = []
        #notes = Note.objects.get(school.pk=school_pk)
        course = Course.objects.get(pk=course_pk)
        print "notes request for course " + str(course.pk) + " by user " + str(user_pk)
        #print jsonifyModel(school, depth=2)
        response_json.append(jsonifyModel(course, depth=1, user_pk=user_pk))
            #response_json.append(school_json)
        print json.dumps(response_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")
    else:
        raise Http404


def all_notes(request):
    """ Display all notes """
    print "using the all_notes view"
    response = {}
    response['schools'] = {}
    for school in School.objects.all():
        print school
        response['schools'][school.name] = {}
        for course in Course.objects.filter(school=school).all():
            print course
            notes = File.objects.filter(course=course).all()
            response['schools'][school.name][course.title] = notes
    print response
    return render(request, 'notes.html', response)


def vote(request, file_pk):
    vote_value = request.GET.get('vote', 0)
    user_pk = request.GET.get('user', -1)
    print "note: " + str(file_pk) + " vote: " + vote_value + "user: " + user_pk

    # Check that GET parameters are valid
    if vote_value != 0 and File.objects.filter(pk=file_pk).exists() and User.objects.filter(pk=user_pk).exists():
        voting_file = File.objects.get(pk=file_pk)
        voting_user = User.objects.get(pk=user_pk)
    else:
        raise Http404

    # If the valid user owns the file or has all ready voted, don't allow voting
    if voting_file.owner == voting_user:
        return HttpResponse("You cannot vote on a file you uploaded")
    # If the valid user has all ready voted, don't allow another vote
    elif voting_file.votes.filter(user=voting_user).exists():
        return HttpResponse("You have all ready voted on this file")
    # Else If the valid user has viewd the file, allow voting
    elif voting_user.get_profile().files.filter(pk=voting_file.pk).exists():
        print "casting vote"
        voting_file.Vote(voter=voting_user, vote_value=vote_value)
        return HttpResponse("success")
    # If valid use does not own file, has not voted, but not viewed the file
    else:
        return HttpResponse("You cannot vote on a file you have not viewed")


''' 
    Search testing
'''
from haystack.query import SearchQuerySet


def search(request):
    results = []
    # Process query and return results
    if request.is_ajax():
        q = request.GET.get("q", "")
        user_pk = request.GET.get("user", "-1")
        print "searching for: " + q + " . User: " + str(user_pk)
        if q != "":
            #Exact match result:
            #results = SearchQuerySet().filter(content__contains=q)
            results = SearchQuerySet().filter(content_auto__contains=q).order_by('django_ct')
            # Partial string matching. Not yet working
            #results = SearchQuerySet().autocomplete(content_auto=q)
            #print results
            if len(results) == 0:
                return HttpResponse("No Results")
            else:
                return TemplateResponse(request, 'search_results.html', {"results": results, "user_pk": int(user_pk)})
        raise Http404
    return render(request, 'search2.html')
