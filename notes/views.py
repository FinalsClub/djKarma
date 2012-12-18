# Copyright (C) 2012  FinalsClub Foundation

import datetime
import json

from ajaxuploader.views import AjaxFileUploader
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
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
from recaptcha.client import captcha as recaptcha

import forms as KarmaForms
#Avoid collision with django.contrib.auth.forms

from notes.gdrive import accept_auth
from KNotes import settings
from templated_email import send_templated_mail

from models import School
from models import Course
from models import Note
from models import Instructor
from models import SiteStats
from models import Level
from models import Vote
from models import ReputationEventType
from models import UsdeSchool
from profile_tasks import tasks
from utils import complete_profile_prompt
from utils import jsonifyModel
from utils import nav_helper
from utils import userCanView


# For Ajax Uploader
import_uploader = AjaxFileUploader()


"""  Static pages, or nearly static pages  """
def about(request):
    response = {}
    response['leader_schools'] = School.objects.order_by('-karma')[:3]
    return render(request, 'n_about.html', response)


def e404(request):
    return render(request, '404.html')


def dashboard(request):
    """ Render the new template style dashboard """
    #print "\nDASHBOARD ----------------------------------------------\n"
    if request.method == "POST":
        # If a user is saving data on the dashboard page
        if 'school' in request.POST:
            user_profile = request.user.get_profile()
            user_profile.school = School.objects.get(name=request.POST['school'])
            user_profile.save()

    response = {}

    response['events'] = request.user.get_profile().reputationEvents.order_by('-id').all()
    response['upload_count'] = Note.objects.filter(owner=request.user).count()

    # Count the reputation events where the user was the actor and the type was 'upvote'
    response['upvote_count'] = request.user.actor.filter(type__title='upvote').count()
    return render(request, 'n_dashboard.html', response)


def home(request):
    """ Landing Page [static] """

    if request.user.is_authenticated():
        return dashboard(request)
    else:
        # Get the 'singleton' SiteStats instance
        stats = SiteStats.objects.get(pk=1)
        #Get recently uploaded files
        recent_files = Note.objects.exclude(title__exact='') \
                .order_by('-timestamp')[:7]
        #print recent_files
        file_count = Note.objects.count()
        return render(request, 'n_home.html',
                {'stats': stats, 'recent_files': recent_files,\
                'file_count': file_count})


def jobs(request):
    ''' Jobs listing page '''
    print "this is the jobs page"
    return render(request, 'n_jobs.html')


def terms(request):
    """ Terms of Service page """
    return render(request, 'n_terms.html')


@login_required
def confirm_email(request, confirmation_code):
    ''' Confirm email
    '''
    user_profile = request.user.get_profile()
    if confirmation_code == user_profile.email_confirmation_code:
        user_profile.email_confirmed = True
        user_profile.save()
        #return HttpResponseRedirect(reverse('profile'))
        return render(request, 'n_email_confirmed.html', {'redirect_url': reverse('dashboard')})
    else:
        return HttpResponse('Invalid email confirmation code.')


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

            new_user = form.save()  # Save the new user from form data
            confirmation_code = new_user.get_profile().setEmailConfirmationCode()
            # TODO: switch to django-templated-email
            activation_link = request.build_absolute_uri(reverse('confirm_email', kwargs={'confirmation_code': confirmation_code}))
            #send_mail(subject='Confirm your email for KarmaNotes.org', message='Please activate your Karma Notes account by following the link below! ' + activation_link, from_email='info@karmanotes.org', recipient_list=[new_user.email], fail_silently=False)

            send_templated_mail(
                template_name='confirm_email',
                from_email='info@karmanotes.org',
                recipient_list=[new_user.email],
                context={
                    'username': new_user.username,
                    'activation_link': activation_link
                },
                # Optional:
                # cc=['cc@example.com'],
                # bcc=['bcc@example.com'],
                # headers={'My-Custom-Header':'Custom Value'},
                # template_prefix="my_emails/",
                template_suffix="email",
            )

            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])  # Authenticate the new user

            login(request, new_user)  # Login in the new user
            return HttpResponseRedirect("/dashboard")
        else:
            return render(request, "registration/register.html", {
        'form': form})
    else:
        form = KarmaForms.UserCreateForm()
        return render(request, "registration/register.html", {'form': form})


""" =====================================================================
    People pages, pages that are heavily customized for a particular user
    ===================================================================== """
@login_required
def raw_file(request, note_pk):
    """ Display the raw html from a Note object for embedding in an iframe """
    note = get_object_or_404(Note, pk=note_pk)
    return HttpResponse(note.html)

""" ===========================================
    Viewing and browsing lists and single pages
    =========================================== """
@login_required
def file(request, note_pk, action=None):
    """ View Note HTML
        Args:
            request: Django request object
            note_pk: file_pk int
            action: last url segment string indicating initial state. i.e: 'edit'
    """
    response = {}
    user_profile = request.user.get_profile()
    file = get_object_or_404(Note, pk=note_pk)

    # If this file is not in the user's collection, 
    # add this file to the user_profile as a viewd file
    if not user_profile.viewed_notes.filter(pk=note_pk).exists():
        # Buy Note viewing privelege for karma
        # award_karma will handle deducting appropriate karma
        user_profile.award_karma('view-file', school=file.school, course=file.course, file=file, user=request.user)
        # Add 'purchased' file to user's collection
        user_profile.viewed_notes.add(file)
        user_profile.save()
        print user_profile, 'purchased', file, 'with karma.'
        # Increment note view count
        file.viewCount += 1
        file.save()

    response['owns_file'] = (file.owner == request.user)
    response['file'] = file

    response['lovable'], response['flagable'] = True, True

    has_voted = file.vote_set.filter(user=request.user).exists()
    response['has_voted'] = has_voted

    if has_voted:
        print 'views.file: current user has voted on this file'
        vote = file.vote_set.get(user=request.user)
        response['vote_status'] = vote.up
        if vote.up:
            response['lovable'] = False
        else:
            response['flagable'] = False

    if action == 'edit':
        #print 'ACTION EDIT'
        response['editing_file'] = True
    else:
        response['editing_file'] = False
        #print 'ACTION NONE'

    return render(request, 'n_note.html', response)


""" ==============
    AJAX endpoints
    ============== """
def fileMeta(request):
    """ Takes async uploaded metadata using the FileMetaDataForm """
    response = {}

    if request.method != "POST":
        # This is the wrong way to use fileMeta, exit
        response["status"] = "invalid"
        return HttpResponse(json.dumps(response), mimetype="application/json")


    form = KarmaForms.FileMetaDataFormNoCaptcha(request.POST)

    if not form.is_valid():
        # Form is invalid
        print form.errors
        print "fileMeta form NOT valid!"
        response["status"] = "invalid"
        #response["form"] = form
        response["message"] = "Please check your form data."
        return HttpResponse(json.dumps(response), mimetype="application/json")

    file = Note.objects.get(pk=form.cleaned_data["file_pk"])
    file.type = form.cleaned_data["type"]
    file.title = form.cleaned_data["title"]
    file.description = form.cleaned_data["description"]
    file.created_on = form.cleaned_data["created_on"]

    if request.user.is_authenticated():
        file.owner = request.user
    else:
        file.owner, _created = User.objects.get_or_create(username=u"KarmaNotes")
        file.owner.save()
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
        request.user.get_profile().add_course(course_id=_course_id)
    # process Tags
    #processCsvTags(file, form.cleaned_data['tags'])
    file.save()
    response = {}
    response["status"] = "success"
    response["file_pk"] = file.pk
    response["karma"] = file.karmaValue()
    #print "fileMeta form valid! " + str(file.pk)
    # lets us use django's messaging system for alert-notifications
    # in our design on upload success at the top of the profile
    # FIXME: fix this message with proper html
    # render an html partial and then send it in json to jquery
    if request.user.is_authenticated():
        messages.add_message(request, messages.SUCCESS,
        "Success! You uploaded a file (message: Django Messaging!")
    # If user is not authenticated, store this file pk in their session
    # TODO: IF a user isn't authenticated - present them
    # an indication that they can claim karma by logging in

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


def school(request, school_query):
    """ View for a school, lists courses and school activity
        :school_query: comes as unicode, if can be int, pass as int
    """
    response = {}
    try:
        school_query = int(school_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    # FIXME: does this work _instead_ or despite of int() casting?
    response['school'], response['courses'] = School.get_courses(school_query)
    return render(request, 'n_school.html', response)

def browse_courses(request, school_query):
    """ View for courses beloging to :school_query:
        :school_query: comes as unicode, if can be int, pass as int
    """
    #response = nav_helper(request)
    response = {}
    try:
        school_query = int(school_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    courses = School.get_courses(school_query)
    if isinstance(courses, tuple):  # FIXME
        response['school'], response['courses'] = courses
        return render(request, 'browse_courses.html', response)
    else:
        raise Http404


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
    # TODO: combine this function with `b_school_course`
    #response = nav_helper(request)
    response = {}
    try:
        course_query = int(course_query)
    except ValueError:
        # cant be cast as an int, so we will search for it as a string
        pass
    course, files = Course.get_notes(course_query, school)
    response['course'], response['files'] = course, files
    # get the users who are members of the course
    response['profiles'] = course.userprofile_set.all()

    # get the karma events associated with the course
    response['events'] = course.reputationevent_set.order_by('-timestamp').all()  # FIXME: possibly order-by
    # we don't use these, FIXME: CLEAN THIS UP
    """
    response['viewed_files'] = request.user.get_profile().viewed_notes.all()

    # FIXME: I don't like this logic one bit, either annotate the db query or fix the schema to NEVER do this
    response['thanked_files'] = []
    response['flagged_files'] = []
    for file in files:
        _vote = file.vote_set.filter(user=request.user)
        if _vote.exists():
            if _vote[0].up: # assuming only one vote result
                response['thanked_files'].append(file.id)
            else:
                response['flagged_files'].append(file.id)
    """

    return render(request, 'n_course.html', response)


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
        file = get_object_or_404(Note, pk=request.POST['file_pk'])
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
    ''' AJAX: add a new course or school
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


def create_course(request):
    """ Form to add a new course to our db
    """

    def custom_validate(form_dict):
        if form_dict['id_title'] == '': return False

    response = {}

    if request.method == 'POST':
        form = KarmaForms.CreateCourseForm(request.POST)

        if form.is_valid():
            user_profile = request.user.get_profile()
            new_course = Course()


            new_course.instructor_email = form.cleaned_data['instructor_email']
            new_course.instructor_name = form.cleaned_data['instructor_name']
            new_course.title = form.cleaned_data['title']
            new_course.desc = form.cleaned_data['desc']
            new_course.school = user_profile.school
            new_course.save()

            user_profile.courses.add(new_course)
            user_profile.save()

        else:
            #TODO: have ajax display error messages
            print "Form is INVALID: %s" % form.errors

    else:
        # request method is NOT POST
        form = KarmaForms.CreateCourseForm()

    return render(request, 'n_lightbox_create_course.html', {'form': form})

@login_required
def add_course_to_profile(request):
    """ ajax endpoint to add a course to a user's profile
        alternatively, to be used when the 'are you in this course' checkbox
        is selected in the upload modal
    """
   #FIXME: this is fragile and ugly
    if request.method == 'POST':
        print "is post"
        user_profile = request.user.get_profile()
        print request.POST
        if 'title' in request.POST:
            title = request.POST['title']
            print "title: %s" % title
            status = user_profile.add_course(course_title=title)
            return HttpResponse(json.dumps({'status': 'success', 'title': title}), mimetype='application/json')
        elif 'id' in request.POST:  # passing the course ID rather than title
            status = user_profile.add_course(course_id=request.POST['id'])
            return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

        else:
            return HttpResponse(json.dumps({'status': 'fail'}), mimetype='application/json')

def drop_course(request):
    #FIXME: drop_course removes a course from a profile, and and add_course_to_profile adds a course
    if request.is_ajax() and request.method == 'POST':
        user_profile = request.user.get_profile()
        course = Course.objects.get(id=request.POST['id'])
        user_profile.courses.remove(course)
        return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

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

def accredited_schools(request):
    """ AJAX: UsdeSchools autocomplete form field """
    print "\nhit accreddited schools view \n\n"
    if request.is_ajax() and request.method == 'POST':
        query = request.POST.get('q')
        print "query: %s" % query
        usde_schools = UsdeSchool.objects.filter(institution_name__icontains=query).distinct()
        print len(usde_schools)
        response = {}
        if len(usde_schools) > 0:
            response['accredited_schools'] = [(school.pk, school.institution_name, school.institution_city, school.institution_state) for school in usde_schools]
            response['status'] = 'success'
        return HttpResponse(json.dumps(response), mimetype="application/json")
    raise Http404


def schools(request):
    """ Ajax: School autcomplete form field """
    if request.is_ajax() and request.method == 'POST' and request.POST.has_key('q'):
        query = request.POST.get('q')
        schools = School.objects.filter(name__icontains=query).distinct()
        response = {}
        if len(schools) > 0:
            response['schools'] = [(school.pk, school.name) for school in schools]
            response['status'] = 'success'
        return HttpResponse(json.dumps(response), mimetype="application/json")
    elif request.method == 'POST':
        # for creating a new school from a form
        # create new school, hasn't been implemented yet
        new_school = School()
        a_school = UsdeSchool.objects.get(id=request.POST['school_id'])
        new_school.name = a_school.institution_name
        new_school.location = u"%s, %s" % (a_school.institution_city, a_school.institution_state)
        new_school.url = a_school.institution_web_address
        new_school.save()
        request.user.get_profile().school = new_school
        request.user.get_profile().save()

        response = {}
        return HttpResponse(json.dumps(response), mimetype="application/json")
    else:
        # render the browse-schools route
        response = {}
        response['schools'] = School.objects.order_by('-karma').all()
        return render(request, 'n_browse_schools.html', response)


    raise Http404

def notes(request):
    """ note list controllers """
    response = {}
    response['notes'] = File.objects.order_by('-numUpVotes').all()
    return render(request, 'n_browse_notes.html', response)

def courses(request, school_query=None):
    """ Ajax: Course autocomplete form field """
    if request.method == 'POST' and request.is_ajax():
        query = request.POST.get('q')
        courses = Course.objects.filter(title__icontains=query, school__name=request.user.get_profile().school).distinct()
        response = {}
        courses = [(course.pk, course.title) for course in courses]
        if len(courses) > 0:
            # if we return more than one course for query, set status
            response['status'] = 'success'
            response['courses'] = courses
        else:
            # if we returned 0 courses for query, return fail
            response['status'] = 'fail'
        return HttpResponse(json.dumps(response), mimetype="application/json")
        # jquery autocomplete 
    elif request.is_ajax():
        # if an ajax call, create a list of indexes and titles
        # used for the autocomplete course field
        response = []
        for course in courses:
            response.append((course.pk, course.title))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    else:
        # when generating a list of all courses to browse
        # browse courses
        # request.method == 'GET'
        response = {}
        response['courses'] = Course.objects.order_by('-karma').all()
        return render(request, 'n_browse_courses.html', response)


    #query = request.GET.get('q')
    #school_pk = request.GET.get('school', 0)
    #courses = Course.objects.filter(title__icontains=query, school=School.objects.get(pk=school_pk)).distinct()
    #courses = Course.objects.filter(title__icontains=query).distinct()

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


@login_required
def vote(request, file_pk):
    vote_value = int(request.POST.get('vote', 0))
    # Validate vote value
    if vote_value not in (-1, 0, 1):
        raise Http404

    print "views.vote (ajax endpoint)"
    print "note:", str(file_pk)
    print "vote:", str(vote_value) 
    print "user:", str(request.user.pk)


    # Check that GET parameters are valid
    voting_file = get_object_or_404(Note, pk=file_pk)
    voting_user = request.user
    user_profile = request.user.get_profile()

    # If the valid user owns the file or has all ready voted, don't allow voting
    if voting_file.owner == request.user:
        print "You cannot vote on a file you uploaded"
        return HttpResponse("You cannot vote on a file you uploaded")

    #If the valid user has all ready voted, don't allow another vote
    elif voting_file.vote_set.filter(user=voting_user) is voting_user:
        print "You have all ready voted on this file"
        return HttpResponse("You have all ready voted on this file")

    # Else If the valid user has viewd the file, allow voting
    elif user_profile.viewed_notes.filter(pk=voting_file.pk).exists():
        print "casting vote"
        voting_file.vote(voter=voting_user, vote_value=vote_value)
        if vote_value == 1:
            return HttpResponse("views.vote: thank recorded")
        elif vote_value == -1:
            return HttpResponse("views.vote: file flagged")
        else:
            return HttpResponse("view.vote: vote cleared")

    # If valid use does not own file, has not voted, but not viewed the file
    else:
        return HttpResponse("You cannot vote on a file you have not viewed")
        print "you cannot vote on a file you have not viewed"

def multisearch(request):
    if request.GET.get("q", "") != "":
        response = {}

        query = request.GET.get("q", "")
        response['query'] = query

        schools = SearchQuerySet().filter(content__icontains=query) \
                    .models(School).load_all()
        response['schools'] = [s.object for s in schools]
        courses = SearchQuerySet().filter(content__icontains=query) \
                    .models(Course).load_all()
        response['courses'] = [c.object for c in courses]
        notes = SearchQuerySet().filter(content__icontains=query) \
                    .models(Note).load_all()
        response['notes'] = [n.object for n in notes]
        response['instructors'] = []
        response['users'] = []

        return render(request, 'n_search_results.html', response)

def browse(request):
    """ Render a page of the schools courses notes that are marked browseable
    """
    response = {}

    #TODO: limit these to less than five each
    response['schools'] = School.objects.filter(browsable=True)
    response['courses'] = Course.objects.filter(browsable=True)
    response['notes'] = Note.objects.filter(browsable=True)
    response['instructors'] = []
    response['users'] = []
    response['browse_all'] = True

    return render(request, 'n_browse_all.html', response)


''' Search testing '''
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
            #results = SearchQuerySet().filter(content__icontains=query).models(Note).highlight()

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

def gdrive_oauth_handshake(request):
    """ Take the oauth authentication_code and finish the oauth2 handshake """
    print "loading gdrive oauth 2"
    print request.GET, dir(request.GET)
    auth_code = request.GET['code']
    print "auth_code:\n"
    print auth_code
    print type(auth_code)
    print dir(auth_code)
    creds = accept_auth(auth_code)
    print creds
    return HttpResponse(creds)
