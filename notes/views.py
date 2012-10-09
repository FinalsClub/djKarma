# Copyright (C) 2012  FinalsClub Foundation

import datetime
import json

from ajaxuploader.views import AjaxFileUploader
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.db.models import Count
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.encoding import iri_to_uri
from haystack.query import SearchQuerySet

import forms as KarmaForms
#Avoid collision with django.contrib.auth.forms

from KNotes import settings

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
from utils import nav_helper
from utils import userCanView

from recaptcha.client import captcha as recaptcha

# For Ajax Uploader
import_uploader = AjaxFileUploader()


"""  Static pages, or nearly static pages  """
def about(request):
    return render(request, 'static/about.html')


def e404(request):
    response = nav_helper(request)
    return render(request, '404.html', response)


def home(request):
    """ Landing Page [static] """

    if request.user.is_authenticated():
        return profile(request)
    else:
        # Get the 'singleton' SiteStats instance
        stats = SiteStats.objects.get(pk=1)
        #Get recently uploaded files
        recent_files = File.objects.exclude(title__exact='') \
                .order_by('-timestamp')[:7]
        #print recent_files
        file_count = File.objects.count()
        return render(request, 'home.html',
                {'stats': stats, 'recent_files': recent_files,\
                'file_count': file_count})


def jobs(request):
    ''' Jobs listing page '''
    return render(request, 'jobs.html')


def terms(request):
    return render(request, 'static/ToS.html')

""" People pages, pages that are heavily customized for a particular user """
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
    response['events'] = request.user.get_profile().reputationEvents.order_by('-timestamp').all()
    return render(request, 'karma-events.html', response)


@login_required
def profile(request):
    """ User Profile """
    response = nav_helper(request)
    response['course_json_url'] = '/jq_course'  # FIXME: replace this with a reverse urls.py query
    response['your_files'] = File.objects.filter(owner=request.user).all()
    return render(request, 'navigation.html', response)


# AJAX
def fileMeta(request):
    """ Takes async uploaded metadata using the FileMetaDataForm """
    response = {}

    if request.method == "POST" and request.is_ajax():
        form = KarmaForms.FileMetaDataFormNoCaptcha(request.POST)
        if form.is_valid():
            file = File.objects.get(pk=form.cleaned_data["file_pk"])
            file.type = form.cleaned_data["type"]
            file.title = form.cleaned_data["title"]
            file.description = form.cleaned_data["description"]
            if request.user.is_authenticated():
                file.owner = request.user
            else:
                file.owner, _created = User.objects.get_or_create(username=u"KarmaNotes")
                # Perform reCAPTCHA check
                if 'recaptcha_challenge' in request.POST and 'recaptcha_response' in request.POST:
                    print 'challenge: ' + str(request.POST['recaptcha_challenge'])
                    print 'response: ' + str(request.POST['recaptcha_response'])
                    print 'private_key: ' + settings.RECAPTCHA_PRIVATE_KEY
                    check_captcha = recaptcha.submit(request.POST['recaptcha_challenge'],
                        request.POST['recaptcha_response'],
                        settings.RECAPTCHA_PRIVATE_KEY, {})
                else:
                    print 'recaptcha keys not found in request.POST'
                    raise Http404

                if not check_captcha.is_valid:
                    print check_captcha.error_code
                    response['status'] = 'invalid'
                    response['message'] = 'Incorrect captcha response. Please try again.'
                    return HttpResponse(json.dumps(response), mimetype="application/json")
            try:
                _school_id = int(form.cleaned_data["school_pk"])
                _course_id = int(form.cleaned_data["course_pk"])
                file.school = School.objects.get(pk=_school_id)
                file.course = Course.objects.get(pk=_course_id)
            except Exception, e:
                print "school/course error: " + str(e)

            if _course_id is not None and form.cleaned_data['in_course'] == "True":
                # if in_course selected, add the course to their profile
                _add_course(request.user.get_profile(), course_id=_course_id)
            # process Tags
            #processCsvTags(file, form.cleaned_data['tags'])
            print "file.save()"
            file.save()
            response = {}
            response["status"] = "success"
            response["file_pk"] = file.pk
            response["karma"] = file.karmaValue()
            print "fileMeta form valid! " + str(file.pk)
            # lets us use django's messaging system for alert-notifications
            # in our design on upload success at the top of the profile
            # FIXME: fix this message with proper html
            if request.user.is_authenticated():
                messages.add_message(request, messages.SUCCESS,
                "Success! You uploaded a file (message: Django Messaging!")
            # If user is not authenticated, store this file pk in their session
            # TODO: IF a user isn't authenticated - present them
            # an indication that they can claim karma by logging in
        else:
            # Form is invalid
            print form.errors
            print "fileMeta form NOT valid!"
            response["status"] = "invalid"
            response["form"] = form
            response["message"] = "Please check your form data."
            return HttpResponse(json.dumps(response), mimetype="application/json")

    else:
        # if not POST or not ajax
        response["status"] = "invalid"
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
                    #schools = School.objects.all().order_by('name').values('name', 'pk')
                    schools = SearchQuerySet().filter(content_auto__contains=search_form.cleaned_data['title']).models(School).values('name', 'pk')
                    print "smartModelQuery: return create School ajaxFormResponse"
                    response = {}
                    response['type'] = 'school'
                    # Django QuerySets are serializable, but when they're empty, error raised
                    if schools is not None and len(schools) > 0:
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
                    if request.POST.get("school", -1) != -1:
                        #print "course at school: " + request.POST.get("school")
                        #courses = Course.objects.filter(school=School.objects.get(pk=int(request.POST.get("school")))).order_by('title').values('title')
                        courses = SearchQuerySet().filter(school=request.POST.get("school"), content_auto__contains=search_form.cleaned_data['title']).models(Course).values('title', 'pk')
                    elif (request.user.is_authenticated() and request.user.get_profile().school is not None):
                        #print "got school from profile"
                        courses = SearchQuerySet().filter(school=request.user.get_profile().school.pk, content_auto__contains=search_form.cleaned_data['title']).models(Course).values('title', 'pk')
                    else:
                        #No school available. Search all schools
                        courses = SearchQuerySet().filter(content_auto__contains=search_form.cleaned_data['title']).models(Course).values('title', 'pk')
                    response = {}
                    response['type'] = 'course'
                     # Django QuerySets are serializable, but when they're empty, error raised
                    if courses is not None and len(courses) > 0:
                        response['suggestions'] = list(courses)
                        response['status'] = 'suggestion'
                    else:
                        response['suggestions'] = []
                        response['status'] = 'no_match'
                    print "smartModelQuery: return create Course suggestion"
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


def browse_schools(request):
    """ Server-side templated browsing of notes by school, course and note """
    response = nav_helper(request)
    # make this order by the most notes in a school
    response['title'] = u"Schools"
    response['schools'] = School.objects.annotate(num_course=Count('course'))\
                .order_by('num_course').reverse().filter(num_course__gt=0).all()
    if request.user.get_profile().school not in response['schools']:
        # create a new list of the user's school, extend it with the current list of schools
        # this prepends the user's school to the top of the school list
        response['schools'] = [request.user.get_profile().school] + list(response['schools'])
        # this converts the QuerySet into a list, so this is not typesafe, but django templates do not care
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
    courses = _get_courses(request, school_query)
    if isinstance(courses, tuple):  # FIXME
        response['school'], response['courses'] = courses
        return render(request, 'browse_courses.html', response)
    else:
        raise Http404


def _get_courses(request, school_query=None):
    """ Private search method.
        :school_query: unicode or int, will search for a the courses with that school matching
        returns: School, Courses+
    """
    if isinstance(school_query, int):
        #_school = School.objects.get_object_or_404(pk=school_query)
        _school = get_object_or_404(School, pk=school_query)
    elif isinstance(school_query, unicode):
        #_school = get_object_or_404(School, name__icontains=school_query)
        #_school = School.objects.filter(name__icontains=school_query).all()[0]
        # FIXME: this ordering might be the wrong way around, if so, remove the '-' from order_by
        _school_q = School.objects.filter(slug=school_query) \
                        .annotate(course_count=Count('course')) \
                        .order_by('-course_count')
        if len(_school_q) != 0:
            _school = _school_q[0]
        else:
            return Http404
    else:
        print "No courses found for this query"
        return Http404
    # if I found a _school
    return _school, Course.objects.filter(school=_school).distinct()


def b_school_course(request, school_query, course_query):
    """ lookup course given course and school names
    """
    # TODO add a url redirect, or an error if the school != course school
    school = get_object_or_404(School, slug=school_query)
    return browse_one_course(request, course_query, school)


def browse_one_course(request, course_query, school):
    """ View for viewing notes from a fuzzy course search
        :course_query: unicode url match, to be type parsed
    """
    response = nav_helper(request)
    try:
        course_query = int(course_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    course, files = _get_notes(request, course_query, school)
    response['course'], response['files'] = course, files
    # get the users who are members of the course
    response['users'] = course.userprofile_set.all()
    # get the karma events associaged with the course
    response['events'] = course.reputationevent_set.order_by('-timestamp').all()  # FIXME: possibly order-by
    response['viewed_files'] = request.user.get_profile().files.all()
    #response['thanked_files'] = [file.id for file in files if request.user in [vote.user for vote in file.votes.all()]]

    # FIXME: I don't like this logic one bit, either annotate the db query or fix the schema to NEVER do this 
    response['thanked_files'] = []
    response['flagged_files'] = []
    for file in files:
        _vote = file.votes.filter(user=request.user)
        if _vote.exists():
            if _vote[0].up: # assuming only one vote result
                response['thanked_files'].append(file.id)
            else:
                response['flagged_files'].append(file.id)

    return render(request, 'browse_one_course.html', response)


def _get_notes(request, course_query, school):
    """ Private search method for a course and it's files
        :course_query:
            if int: Course.pk
            if unicode: Course.title
        returns Course, Notes+
    """
    if isinstance(course_query, int):
        _course = get_object_or_404(Course, pk=course_query)
    elif isinstance(course_query, unicode):
        _course = get_object_or_404(Course, slug=course_query, school=school)
    else:
        print "No course found, so no notes"
        return Http404
    return _course, File.objects.filter(course=_course).distinct()



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
            response['school_pk'] = user_profile.school.pk
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


@login_required
def editFileMeta(request):
    ''' Handles AJAX requests to edit file meta data.
        Now, just title and description
    '''
    if request.is_ajax() and 'file_pk' in request.POST:
        file = get_object_or_404(File, pk=request.POST['file_pk'])
        if request.user == file.owner:
            do_save = False
            response = {}
            if 'title' in request.POST:
                form = KarmaForms.GenericCharForm({"text": request.POST['title']})
                if form.is_valid():
                    file.title = form.cleaned_data['text']
                    response['title'] = form.cleaned_data['text']
                    do_save = True
            if 'description' in request.POST:
                form = KarmaForms.GenericCharForm({"text": request.POST['description']})
                if form.is_valid():
                    file.description = form.cleaned_data['text']
                    response['description'] = form.cleaned_data['text']
                    do_save = True
            if do_save:
                file.save()
                response['status'] = 'success'
                return HttpResponse(json.dumps(response), mimetype="application/json")
            else:
                return HttpResponse(json.dumps({"status": "no input"}), mimetype="application/json")
    
    raise Http404

@login_required
def editCourseMeta(request):
    ''' Handles AJAX requests to edit course meta data.
        Now, just title and professor
    '''
    if request.is_ajax() and 'course_pk' in request.POST:
        course = get_object_or_404(Course, pk=request.POST['course_pk'])
        # TODO: Create site-wide karma constants tied to privileges
        if request.user.get_profile().karma > 200:
            do_save = False
            response = {}
            if 'title' in request.POST:
                form = KarmaForms.GenericCharForm({"text": request.POST['title']})
                if form.is_valid():
                    course.title = form.cleaned_data['text']
                    response['title'] = form.cleaned_data['text']
                    do_save = True
            if 'professor' in request.POST:
                form = KarmaForms.GenericCharForm({"text": request.POST['professor']})
                if form.is_valid():
                    # If a professor by the name given doesn't exist
                    # Create a new model. TODO: provide suggestions before model creation
                    try:
                        professor = Instructor.objects.filter(name__icontains=form.cleaned_data['text'])[0]
                    except:
                        professor = Instructor.objects.create(name=form.cleaned_data['text'], school=request.user.get_profile().school)
                        # TODO: Index Instructors and search -> return suggestions? Ugh :)
                    course.professor = professor
                    # get_or_create professor here!
                    response['professor'] = professor.name
                    do_save = True
            if do_save:
                course.save()
                response['status'] = 'success'
                return HttpResponse(json.dumps(response), mimetype="application/json")
            else:
                return HttpResponse(json.dumps({"status": "no input"}), mimetype="application/json")

    raise Http404


@login_required
def addModel(request):
    ''' This replaces addCourseOrSchool in the new
        modal-upload process
    '''
    if request.is_ajax() and request.method == 'POST':
        if 'type' in request.POST:
            type = request.POST['type']
            form = KarmaForms.ModelSearchForm(request.POST)
            if form.is_valid():
                if type == "course" and request.user.get_profile().school != None:
                    new_model = Course.objects.create(title=form.cleaned_data['title'], school=request.user.get_profile().school)
                    # add the newly created course to the requesting user's profile
                    request.user.get_profile().courses.add(new_model)
                elif type == "school":
                    new_model = School.objects.create(name=form.cleaned_data['title'])
                return HttpResponse(json.dumps({'type': type, 'status': 'success', 'new_pk': new_model.pk}), mimetype='application/json')
    raise Http404

@login_required
def add_course_to_profile(request):
    """ ajax endpoint to add a course to a user's profile
        alternatively, to be used when the 'are you in this course' checkbox
        is selected in the upload modal
    """
    if request.is_ajax() and request.method == 'POST':
        print "this is the add_course request\n\t %s" % request.POST
        user_profile = request.user.get_profile()
        status = _add_course(user_profile, course_title=request.POST['title'])
        if status:
            return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')
        else:
            print "There was an error adding a course to a profile"
            print "\t profile: %s %s, course: %s" % (user_profile, user_profile.id, request.POST['title'])

def _add_course(user_profile, course_title=None, course_id=None):
    """ Helper function to add a course to a userprofile
        for avoiding duplicate code
        :user_profile: `notes.models.UserProfile`
        :course_title:    `notes.models.Course.title`
        :course_id:    `notes.models.Course.id`
    """
    # FIXME: add conditional logic to see if course is already added and error handling
    if course_title is not None:
        course = Course.objects.get(title=course_title)
    elif course_id is not None:
        course = Course.objects.get(pk=course_id)
    else:
        print "[_add_course]: you passed neither a course_title nor a course_id, \
        nothing to add"
        return False
    user_profile.courses.add(course) # implies save()
    return True


def register(request, invite_user):
    """ Display user login and signup screens
        the registration/login.html template redirects login attempts
        to django's built-in login view (django.contrib.auth.views.login).
        new user registration is handled by this view (because there is no built-in)
    """
    # TODO: use give the invite_user some karma for referring someone
    if request.method == 'POST':
        #Fill form with POSTed data
        form = KarmaForms.UserCreateForm(request.POST)
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
        form = KarmaForms.UserCreateForm()
        return render(request, "registration/register.html", {'form': form})


"""
    AJAX views
"""


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
    if True:  # FIXME: why is this True here?
        query = request.GET.get('q')
        school_pk = request.GET.get('school', 0)
        # If no school provided, search all courses
        if int(school_pk) == 0:
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
    response = [(course.id, course.title) for course in courses]
    print json.dumps(response)
    return HttpResponse(json.dumps(response), mimetype="application/json")



def nurl_file(request, school_query, course_query, file_id, action=None):
    return file(request, file_id, action)


@login_required
def file(request, note_pk, action=None):
    """ View Note HTML 
        Args:
            request: Django request object
            note_pk: file_pk int
            action: last url segment string indicating initial state. i.e: 'edit'
    """

    # Check that user has permission to read
    #profile = request.user.get_profile()
    response = nav_helper(request)
    user = request.user
    try:
        profile = user.get_profile()
    except:
        raise Http404
    # If the user does not have read permission, and the
    # Requested files is not theirs
    '''
    if not profile.can_read and not userCanView(request.user, File.objects.get(pk=note_pk)):
        #file_denied(request, note_pk)
        pass
    '''
    try:
        file = File.objects.get(pk=note_pk)
    except:
        raise Http404
    # Increment note view count
    file.viewCount += 1
    file.save()

    # If this file is not in the user's collection, karmic purchase occurs
    #if file not in profile.files.all():
    if(not userCanView(user, File.objects.get(pk=note_pk))):
        # Buy Note viewing privelege for karma
        # awardKarma will handle deducting appropriate karma
        profile.awardKarma('view-file', school=profile.school, course=file.course, file=file)
        # Add 'purchased' file to user's collection
        profile.files.add(file)
        profile.save()

    # This is ugly, but is needed to be able to get the note type full name
    file_type = [t[1] for t in file.FILE_TYPES if t[0] == file.type][0]
    url = iri_to_uri(file.file.url)
    response['owns_file'] = (file.owner == request.user)
    response['file'] = file
    response['file_type'] = file_type
    response['url'] = url

    if action == 'edit':
        #print 'ACTION EDIT'
        response['editing_file'] = True
    else:
        response['editing_file'] = False
        #print 'ACTION NONE'

    return render(request, 'view-file.html', response)


def file_denied(request, note_pk):
    """ What we show someone who is not allowed to view a file
        NOTE: Not currently used
        :request:   django request object
        :note_pk:   id of the file/note
    """
    user_karma = profile.karma
    level = Level.objects.get(title='Prospect')
    print level.karma
    progress = (user_karma / float(level.karma)) * 100
    return TemplateResponse(request, 'karma_wall.html', {'required_level': level, 'progress': progress, 'permission': 'access files'})


def searchBySchool(request):
    """ Ajax: Return user's school's courses in JSON
        Used by search page javascript.
        If user has no school, show all schools
    """
    response_json = []

    if request.is_ajax():
        if request.user.is_authenticated and request.user.get_profile().school is not None:
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
    vote_value = int(request.POST.get('vote', 0))
    # Validate vote value
    if not (vote_value == 0 or vote_value == -1 or vote_value == 1):
        raise Http404

    print "note: " + str(file_pk) + " vote: " + str(vote_value) + "user: " + str(request.user.pk)

    # Check that GET parameters are valid
    if vote_value != 0 and File.objects.filter(pk=file_pk).exists():
        voting_file = File.objects.get(pk=file_pk)
        voting_user = request.user
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
        if vote_value == 1:
            return HttpResponse("thank recorded")
        elif vote_value == -1:
            return HttpResponse("file flagged")
    # If valid use does not own file, has not voted, but not viewed the file
    else:
        return HttpResponse("You cannot vote on a file you have not viewed")


'''
    Search testing
'''


def search(request):
    results = []
    # Process query and return results
    if request.GET.get("q", "") != "":
        query = request.GET.get("q", "")
        user_pk = request.GET.get("user", "-1")
        print "searching for: " + query + " . User: " + str(user_pk)
        if query != "":
            #Exact match result. Highlighting works!
            #results = SearchQuerySet().filter(content__icontains=query).highlight()

            #Exact match results w/Highlighting. Target notes
            #results = SearchQuerySet().filter(content__icontains=query).models(File).highlight()

            #highlight = Highlighter(query)
            #highlight_test = highlight.highlight('this is a test ' + query + 'yes, a test')

            #Partial match result. Works, but w/out highlighting
            results = SearchQuerySet().filter(content_auto__contains=query).order_by('django_ct')

            # Partial string matching. Not yet working
            #results = SearchQuerySet().autocomplete(content_auto=query).highlight()
            #print results
            return render(request, 'search_results2.html', {'results': results, 'query': query})
            '''
            For 'old' ajax search:
            if len(results) == 0:
                #return HttpResponse("No Results")
            else:
                #return TemplateResponse(request, 'search_results.html', {"results": results, "user_pk": int(user_pk)})
            '''
        raise Http404
    raise Http404


def captcha(request):
    ''' For now, the only action the server needs to
        take on each invocation of the modal-upload form
        is to generate a new math captcha answer
    '''
    form = KarmaForms.CaptchaForm()
    return TemplateResponse(request, 'captcha.html', {'form': form})


