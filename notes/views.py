# Copyright (C) 2012  FinalsClub Foundation

import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.encoding import iri_to_uri
from ajaxuploader.views import AjaxFileUploader

import forms as KarmaForms
#Avoid collision with django.contrib.auth.forms

from models import School
from models import Course
from models import File
from models import Instructor
from models import SiteStats
from models import Level
from models import Vote
from models import ReputationEventType
from profile_tasks import tasks
from utils import complete_profile_prompt
from utils import jsonifyModel
from utils import processCsvTags
from utils import userCanView

import datetime

#from django.core import serializers

## :|: Static pages :|: &
def home(request):
    """ Landing Page [static] """

    if request.user.is_authenticated():
        return profile(request)
    else:
        # Get the 'singleton' SiteStats instance
        stats = SiteStats.objects.get(pk=1)

        #Get recently uploaded files
        recent_files = File.objects.exclude(title__exact='').order_by('-timestamp')[:7]
        #print recent_files

        return render(request, 'home.html', {'stats': stats, 'recent_files': recent_files})

def about(request):
    return render(request, 'static/about.html')

def terms(request):
    return render(request, 'static/ToS.html')

## :|: Uploading :|: &

# For Ajax Uploader
import_uploader = AjaxFileUploader()


def fileMeta(request):
    """ Takes async uploaded metadata using the FileMetaDataForm """
    response = {}

    if request.method == "POST" and request.is_ajax():
        form = KarmaForms.FileMetaDataFormNoCaptcha(request.POST)
        if form.is_valid():
            file = File.objects.get(pk=form.cleaned_data["file_pk"])
            file.type = form.cleaned_data["type"]
            file.title = form.cleaned_data["title"]
            file.descriptioin = form.cleaned_data["description"]
            try:
                file.school = School.objects.get(pk=int(form.cleaned_data["school_pk"]))
                file.course = Course.objects.get(pk=int(form.cleaned_data["course_pk"]))
            except Exception, e:
                print "school/course error: " + str(e)
            # process Tags
            #processCsvTags(file, form.cleaned_data['tags'])
            file.save()
            response = {}
            response["status"] = "success"
            response["file_pk"] = file.pk
            print "fileMeta form valid! " + str(file.pk)
            if request.user.is_authenticated():
                # This should let us use django's messaging system to do the alert-notifications
                # in our design on upload success at the top of the profile
                # FIXME: fix this message with proper html
                messages.add_message(request, messages.SUCCESS, "Success! You uploaded a file (message brought to you by Django Messaging!")
        else:
            # Form is invalid
            print "fileMeta form NOT valid!"
            response["status"] = "invalid"
            response["form"] = form
            response["message"] = "Please check your form data."
            return TemplateResponse(request, 'ajaxFormResponse_min.html', response)

    else:
        # if not POST or not ajax
        response["status"] = "invalid request"
    return HttpResponse(json.dumps(response), mimetype="application/json")


def smartModelQuery(request):
    """ Accessed by charfields corresponding to a model title/name
        See if model with similiar title exists and return title
        If not, return model create form with populated title/name
    """
    if request.method == 'POST' and request.is_ajax():
        print "title: " + str(request.POST['title']) + ' type: ' + str(request.POST['type'])
        search_form = KarmaForms.ModelSearchForm(request.POST)
        if search_form.is_valid():
            if request.POST['type'] == "school":
                # If no school matching text entry exists, present School Form
                if not School.objects.filter(name=search_form.cleaned_data['title']).exists():
                    # Return a list of all schools to present to user, ensuring duplicate entires aren't made
                    # TODO: Try searching school name with input, return mathing results
                    schools = School.objects.all().order_by('name').values('name', 'pk')
                    print "smartModelQuery: return create School ajaxFormResponse"
                    response = {}
                    response['type'] = 'school'
                    # Django QuerySets are serializable, but when they're empty, error raised
                    if schools != None:
                        response['suggestions'] = list(schools)
                        response['status'] = 'suggestion'
                    else:
                        response['suggestions'] = []
                        response['status'] = 'no_match'
                    return HttpResponse(json.dumps(response), mimetype="application/json")
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
            if request.POST['type'] == "course":
                # If no course matching text entry exists, present Course Form
                if not Course.objects.filter(title=search_form.cleaned_data['title']).exists():
                    courses = None
                    if request.GET.get("school", -1) != -1:
                        courses = Course.objects.filter(school=School.objects.get(pk=request.GET.get("school"))).order_by('title')
                    response = {}
                    response['type'] = 'course'
                     # Django QuerySets are serializable, but when they're empty, error raised
                    if courses != None:
                        response['suggestions'] = list(courses)
                        response['status'] = 'suggestion'
                    else:
                        response['suggestions'] = []
                        response['status'] = 'no_match'
                    print "smartModelQuery: return create Course sugesstions"
                    return HttpResponse(json.dumps(response), mimetype="application/json")
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
        else:
            print search_form.errors
    raise Http404


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
    response['share_url'] = u"http://karmanotes.org/sign-up/{0}".format(user_profile.getName())
    response['user_profile'] = user_profile
    response = get_upload_form(response)

    # home built auto-complete
    if not user_profile.school:
        response['available_schools'] = [(str(school.name), school.pk) for school in School.objects.all().order_by('name')]
    if not user_profile.grad_year:
        response['available_years'] = range(datetime.datetime.now().year, datetime.datetime.now().year + 10)

    return response

def your_courses(request):
    """ List a user's courses on a profile-like page using django templates """
    response = nav_helper(request)
    response['courses'] = request.user.get_profile().courses.all()
    return render(request, 'your-courses.html', response)

def browse_schools(request):
    """ Server-side templated browsing of notes by school, course and note """
    response = nav_helper(request)
    # make this order by the most notes in a school
    response['title'] = u"Schools"
    response['schools'] = School.objects.annotate(num_course=Count('course')).order_by('num_course').reverse().all()
    return render(request, 'browse_schools.html', response)

    
def browse_courses(request, school_query):
    """ View for courses beloging to :school_query:
        :school_query: comes as unicode, if can be int, pass as int
    """
    response = nav_helper(request)
    try:
        school_query = int(school_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    # pass the school query to 
    response['school'], response['courses'] = _get_courses(request, school_query)
    return render(request, 'browse_courses.html', response)

def _get_courses(request, school_query=None):
    """ Private search method.
        :school_query: unicode or int, will search for a the courses with that school matching
        returns: School, Courses+
    """
    if isinstance(school_query, int):
        #_school = School.objects.get_object_or_404(pk=school_query)
        _school = get_object_or_404(School, pk=school_query)
    elif isinstance(school_query, unicode):
        #_school = School.objects.get(name__icontains=school_query)
        _school = get_object_or_404(School, name__icontains=school_query)
    else:
        print "No courses found for this query"
        return Http404
    # if I found a _school
    return _school, Course.objects.filter(school=_school).distinct()

def browse_one_course(request, course_query):
    """ View for viewing notes from a fuzzy course search
        :course_query: unicode url match, to be type parsed
    """
    response = nav_helper(request)
    try:
        course_query = int(course_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    # pass the school query to 
    response['course'], response['files'] = _get_notes(request, course_query)
    print response['course']
    return render(request, 'browse_one_course.html', response)

def _get_notes(request, course_query):
    """ Private search method for a course and it's files
        :course_query: 
            if int: Course.pk
            if unicode: Course.title
        returns Course, Notes+
    """
    if isinstance(course_query, int):
        _course = get_object_or_404(Course, pk=school_query)
    elif isinstance(course_query, unicode):
        _course = get_object_or_404(Course, title__icontains=course_query)
    else:
        print "No course found, so no notes"
        return Http404
    return _course, File.objects.filter(course=_course).distinct()

def getting_started(request):
    """ View for introducing a user to the site and asking them to accomplish intro tasks """
    response = nav_helper(request)
    response['tasks'] = []
    for task in tasks:
        t = {}
        t['message'] = task().message
        t['status'] = task().check(request.user.get_profile())
        t['karma'] = task().karma
        response['tasks'].append(t)
    return render(request, 'getting-started.html', response)


def karma_events(request):
    """ Shows a time sorted log of your events that affect your 
        karma score positively or negatively. 
    """
    # navigation.html
    response = nav_helper(request)
    response['events'] = request.user.get_profile().reputationEvents.all()
    return render(request, 'karma-events.html', response)


@login_required
def profile(request):
    """ User Profile """
    response = nav_helper(request)

    response['course_json_url'] = '/jq_course' # FIXME: replace this with a reverse urls.py query
    return render(request, 'navigation.html', response)

@login_required
def editProfile(request):
    ''' Handles AJAX requests to edit the user's profile.
    '''
    if(request.is_ajax()):
        response = {}
        do_save = False
        user_pk = request.user.pk
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
    response['school_form'] = KarmaForms.SmartSchoolForm
    return response


def addModel(request):
    ''' This replaces addCourseOrSchool in the new
        modal-upload process
    '''
    if request.is_ajax() and request.method == 'POST':
        if 'type' in request.POST:
            type = request.POST['type']
            form = KarmaForms.ModelSearchForm(request.POST)
            if form.is_valid():
                if type == "course":
                    new_model = Course.objects.create(title=form.cleaned_data['title'])
                elif type == "school":
                    new_model = School.objects.create(name=form.cleaned_data['title'])

                return HttpResponse(json.dumps({'type': type, 'status': 'success', 'new_pk': new_model.pk}), mimetype='application/json')
    raise Http404

def register(request, invite_user):
    """ Display user login and signup screens
        the registration/login.html template redirects login attempts
        to django's built-in login view (django.contrib.auth.views.login).
        new user registration is handled by this view (because there is no built-in)
    """
    # TODO: use give the invite_user some karma for referring someone
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

'''
    AJAX views
'''

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


def courses(request, school_query=None):
    """ Ajax: Course autocomplete form field """

    # Find courses, or school and courses
    if True: # FIXME: why is this True here?
        query = request.GET.get('q')
        school_pk = request.GET.get('school', 0)
        # If no school provided, search all courses
        if school_pk == 0:
            courses = Course.objects.filter(title__icontains=query).distinct()
        # IF school provided, restrict search
        else:
            courses = Course.objects.filter(title__icontains=query, school=School.objects.get(pk=school_pk)).distinct()

    if request.is_ajax():
        # if an ajax call, create a list of indexes and titles
        response = []
        for course in courses:
            response.append((course.pk, course.title))
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


@login_required
def file(request, note_pk):
    """ View Note HTML """
    # Check that user has permission to read
    #profile = request.user.get_profile()
    user = request.user
    try:
        profile = user.get_profile()
    except:
        raise Http404
    # If the user does not have read permission, and the
    # Requested files is not theirs
    if not profile.can_read and not userCanView(request.user, File.objects.get(pk=note_pk)):
        user_karma = profile.karma
        level = Level.objects.get(title='Prospect')
        print level.karma
        progress = (user_karma / float(level.karma)) * 100
        return TemplateResponse(request, 'karma_wall.html', {'required_level': level, 'progress': progress, 'permission': 'access files'})
    try:
        file = File.objects.get(pk=note_pk)
    except:
        raise Http404
    # Increment note view count
    file.viewCount += 1
    file.save()

    # If this file is not in the user's collection, karmic purchase occurs
    if(not userCanView(user, File.objects.get(pk=note_pk))):
        # Buy Note viewing privelege for karma
        # awardKarma will handle deducting appropriate karma
        profile.awardKarma('view-file')
        # Add 'purchased' file to user's collection
        profile.files.add(file)
        profile.save()

    # This is ugly, but is needed to be able to get the note type full name
    file_type = [t[1] for t in file.FILE_TYPES if t[0] == file.type][0]
    url = iri_to_uri(file.file.url)
    return TemplateResponse(request, 'view-file.html', {'file': file, 'file_type': file_type, 'url': url})


def searchBySchool(request):
    """ Ajax: Return user's school's courses in JSON
        Used by search page javascript.
        If user has no school, show all schools
    """
    response_json = []

    if request.is_ajax():
        if request.user.is_authenticated and request.user.get_profile().school != None:
            school = get_object_or_404(School, pk=request.user.get_profile().school.pk)
            response_json.append(jsonifyModel(model=school, depth=1))
        else:
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
        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = -1
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
        #print json.dumps(response_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")
    else:
        raise Http404


@login_required
def vote(request, file_pk):
    vote_value = request.GET.get('vote', 0)
    user_pk = request.user.pk
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
    if request.GET.get("q", "") != "":
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
    raise Http404


def captcha(request):
    ''' For now, the only action the server needs to 
        take on each invocation of the modal-upload form
        is to generate a new math captcha answer
    '''
    form = KarmaForms.CaptchaForm()
    return TemplateResponse(request, 'captcha.html', {'form': form})
