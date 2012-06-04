# Copyright (C) 2012  FinalsClub Foundation

import json

from django import forms as djangoforms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.encoding import iri_to_uri
from simple_autocomplete.widgets import AutoCompleteWidget

from forms import UploadFileForm
from forms import UsherUploadFileForm
from forms import UsherCourseForm
from forms import ModelSearchForm
from forms import TypeTagsForm
from forms import CourseForm
from forms import SchoolForm
from forms import InstructorForm
from forms import ProfileForm
from gdocs import convertWithGDocsv3
from models import School
from models import Course
from models import File
from models import Instructor
from models import SiteStats
from models import Level
from models import Vote
from utils import jsonifyModel, processCsvTags, uploadForm

#from django.core import serializers

## :|: Static pages :|: &
def home(request):
    """ Landing Page [static] """
    # Get the 'singleton' SiteStats instance
    stats = SiteStats.objects.get(pk=1)

    #Get recently uploaded files
    recent_files = File.objects.order_by('-timestamp')[:7]

    return render(request, 'home.html', {'stats': stats, 'recent_files': recent_files})


def about(request):
    print "loading the about page"
    return render(request, 'static/about.html')

## :|: Uploading :|: &
@login_required
def uploadUsher(request):
    """ Upload Usher
        Guides user through upload process
        Aims to minimize process
    """
    template_data = {}
    #template_data['course_form'] = CourseForm()
    #template_data['school_form'] = SchoolForm()
    #template_data['instructor_form'] = InstructorForm()
    template_data['user_school'] = request.user.get_profile().school
    template_data['search_form'] = ModelSearchForm
    template_data['file_form'] = UsherUploadFileForm()

    # If File Upload form is submitted
    if request.method == 'POST':
        file_form = UsherUploadFileForm(request.POST, request.FILES)
        # 'type' used to generate ajaxFormResponse.html
        template_data['type'] = "File"
        # It should be safe to use POST['school'] and POST['course']. Validated by addCourseOrSchool or SmartModelQuery
        template_data['school_title'] = School.objects.get(pk=int(request.POST['school'])).name
        template_data['course_title'] = Course.objects.get(pk=int(request.POST['course'])).title
        if file_form.is_valid():
            newNote = File.objects.create(
                                type=file_form.cleaned_data['type'],
                                title=file_form.cleaned_data['title'],
                                description=file_form.cleaned_data['description'],
                                course=file_form.cleaned_data['course'],
                                school=file_form.cleaned_data['school'],
                                #instructor=form.cleaned_data['instructor'],
                                file=request.FILES['note_file'])

            # Get or Create a Tag for each 'tag' given in the CharField (as csv)
            processCsvTags(newNote, file_form.cleaned_data['tags'])

            # The below line is used if Tags is data from a ModelMultipleChoiceField
            #newNote.tags = form.cleaned_data['tags']

            # A bound Form is immutable, so to provide the hidden field values
            # Which aren't passed on (Because the hidden fields are Charfields converted to Models on clean())
            # We'll pass them to the template directly and inject into form with javascript
            template_data['school'] = request.POST['school']
            template_data['course'] = request.POST['course']
            try:
                # TESTING: Uncomment pass, comment convertWithGDocs(newNote) to disable Google Documents processing
                #pass
                # DEPRECATED: Google Docs API v2
                #convertWithGDocs(newNote)

                convertWithGDocsv3(newNote)
            except Exception, e:
                print "Google Documents API error: " + str(e)
                # TODO: More granular exception handling
                newNote.delete()

                template_data['file_form'] = file_form
                template_data['message'] = "We're sorry, there was a problem processing your file. Can you convert it to a .doc or .rtf?"
                return render(request, 'uploadUsher.html', template_data)

            # After the document is accepted by Google Documents, credit the user
            # addFile adds the file to the user's collection, sets the file owner
            # to the user, generates the appropriate ReputationEvent and handles corresponding karma transaction
            user_profile = request.user.get_profile()
            user_profile.addFile(newNote)

            # Return bound form and success message
            template_data['file_form'] = file_form
            template_data['message'] = "File successfully uploaded! Your Karma increases!"
            return render(request, 'uploadUsher.html', template_data)
        # Form invalid
        else:
            print file_form.errors
            # A bound Form is immutable, so to provide the hidden field values
            # Which aren't passed on (Because the hidden fields are Charfields converted to Models on clean())
            # We'll pass them to the template directly and inject into form with javascript
            template_data['school'] = request.POST['school']
            template_data['course'] = request.POST['course']

            template_data['file_form'] = file_form
            template_data['message'] = "Please check your form data."
            return render(request, 'uploadUsher.html', template_data)
    # If GET: Begin Upload Usher
    else:
        return render(request, 'uploadUsher.html', template_data)


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
                    return TemplateResponse(request, 'ajaxFormResponse.html', {'form': form, 'type': request.POST['type'], 'message': message, 'suggestions': schools})
                # A school matching entry exists
                else:
                    # Return a json object: {'status': 'success', 'model': model's pk}
                    response = {}
                    response['status'] = 'success'
                    response['model'] = School.objects.get(name=search_form.cleaned_data['title']).pk
                    return HttpResponse(json.dumps(response), mimetype="application/json")
            if request.POST['type'] == "Course":
                # If no course matching text entry exists, present Course Form
                if not Course.objects.filter(title=search_form.cleaned_data['title']).exists():
                    form = UsherCourseForm(initial={'title': search_form.cleaned_data['title']})
                    message = "Tell us a little more about your course"
                    courses = None
                    if request.GET.get("school", -1) != -1:
                        courses = Course.objects.filter(school=School.objects.get(pk=request.GET.get("school"))).values("title", "pk").order_by('title')
                    #courses = Course
                    return TemplateResponse(request, 'ajaxFormResponse.html', {'form': form, 'type': request.POST['type'], 'message': message, 'suggestions': courses})
                # A course matching entry exists
                else:
                    # Return a json object: {'status': 'success', 'model': 'model's pk, 'model_title': title}
                    response = {}
                    response['status'] = 'success'
                    response_course = Course.objects.get(title=search_form.cleaned_data['title'])
                    response['model'] = response_course.pk
                    response['model_title'] = response_course.title
                    return HttpResponse(json.dumps(response), mimetype="application/json")
    raise Http404


@login_required
def upload(request):
    """ Upload Page
        If user is authenticated, home view should be upload-notes page
        Else go to login page

        If a note has been uploaded (POST request), process it and report success.
        Return user to upload screen
    """

    course_form = CourseForm()
    school_form = SchoolForm()
    instructor_form = InstructorForm()

    if request.method == 'POST':
        file_form = UploadFileForm(request.POST, request.FILES)

        if file_form.is_valid():
            newNote = File.objects.create(
                                type=file_form.cleaned_data['type'],
                                title=file_form.cleaned_data['title'],
                                description=file_form.cleaned_data['description'],
                                course=file_form.cleaned_data['course'],
                                school=file_form.cleaned_data['school'],
                                #instructor=form.cleaned_data['instructor'],
                                file=request.FILES['note_file'])

            # Get or Create a Tag for each 'tag' given in the CharField (as csv)
            processCsvTags(newNote, file_form.cleaned_data['tags'])

            # The below line is used if Tags is data from a ModelMultipleChoiceField
            #newNote.tags = form.cleaned_data['tags']
            try:
                # TESTING: Uncomment pass, comment convertWithGDocs(newNote) to disable Google Documents processing
                #pass
                #convertWithGDocs(newNote)
                convertWithGDocsv3(newNote)
            except Exception, e:
                print "gDocs error: " + str(e)
                # TODO: More granular exception handling
                newNote.delete()
                return render(request, 'upload.html', {'message': 'We\'re having trouble working with your file. Please ensure it has a file extension (i.e .doc, .rtf)', 'file_form': file_form, 'course_form': course_form, 'school_form': school_form, 'instructor_form': instructor_form})

            # After the document is accepted by convertWithGDocs, credit the user
            user_profile = request.user.get_profile()
            # Credit the user with this note. See models.UserProfile.addFile
            user_profile.addFile(newNote)
            return render(request, 'upload.html', {'message': 'File Successfully Uploaded! Add another!', 'file_form': file_form, 'course_form': course_form, 'school_form': school_form, 'instructor_form': instructor_form})
        else:
            return render(request, 'upload.html', {'message': 'Please check your form entries.', 'file_form': file_form, 'course_form': course_form, 'school_form': school_form, 'instructor_form': instructor_form})
    #If a note has not been uploaded (GET request), show the upload form.
    else:
        # uploadForm() pre-populates the School field with the user
        file_form = uploadForm(request.user)
        return render(request, 'upload.html', {'file_form': file_form, 'course_form': course_form, 'school_form': school_form, 'instructor_form': instructor_form})


@login_required
def profile(request):
    """ User Profile """
    # If user profile data has been submitted:
    if request.method == 'POST':
            #This must go before profile data calc
            profile_form = ProfileForm(request.POST)
            if profile_form.is_valid():
                # Update user profile with form data
                # Karma points will be added as necessary
                # By UserProfile model
                profile = request.user.get_profile()
                profile.school = profile_form.cleaned_data['school']
                #print "grad_year " + str(profile_form.cleaned_data['grad_year'])
                if not profile_form.cleaned_data['grad_year'] == "":
                    profile.grad_year = profile_form.cleaned_data['grad_year']
                profile.save()

    # Calculate User's progress towards next Karma level
    # Depends on models.Level objects
    user_karma = request.user.get_profile().karma
    levels = Level.objects.all()

    next_level = None
    for level in levels:
        if user_karma < level.karma:
            next_level = level
            break

    # The user has reached the top level
    if not next_level:
        progress = 100
    else:
        progress = (user_karma / float(next_level.karma)) * 100

    #Pre-populate ProfileForm with user's data
    profile_data = {}
    recent_files = []
    if request.user.get_profile().school != None:
        profile_data['school'] = request.user.get_profile().school

        # If user has a school selected, fetch recent additions to School
        # For the user's news feed
        recent_files = File.objects.filter(school=request.user.get_profile().school).order_by('-timestamp')[:5]
    if request.user.get_profile().grad_year != None:
        profile_data['grad_year'] = request.user.get_profile().grad_year

    # The profile form has been submitted with updated profile info
    if request.method == 'POST':
        if not profile_form.is_valid():
            # Return profile page with form + errors
            return render(request, 'profile.html', {'progress': int(progress), 'next_level': next_level, 'profile_form': profile_form, 'recent_files': recent_files})
    else:
        # If GET, Populate Profileform with existing profile data
        profile_form = ProfileForm(initial=profile_data)

    return render(request, 'profile.html', {'progress': int(progress), 'next_level': next_level, 'profile_form': profile_form, 'recent_files': recent_files})


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
                response['model'] = model.pk

                if type == "Course":
                    response['model_title'] = model.title
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


def register(request):
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


def courses(request):
    """ Ajax: Course autocomplete form field """
    if request.is_ajax():
        query = request.GET.get('q')
        school_pk = request.GET.get('school', '0')
        # If no school provided, search all courses
        if school_pk == 0:
            courses = Course.objects.filter(title__icontains=query).distinct()
        # IF school provided, restrict search
        else:
            courses = Course.objects.filter(title__icontains=query, school=School.objects.get(pk=school_pk)).distinct()
        response = []
        for course in courses:
            response.append((course.pk, course.title))
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
    if not profile.can_read and not profile.files.filter(pk=note_pk).exists():
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
    if(not profile.files.filter(pk=note.pk).exists()):
        # Buy Note viewing privelege for karma
        # awardKarma will handle deducting appropriate karma
        profile.awardKarma('view-file')
        # Add 'purchased' file to user's collection
        profile.files.add(note)
        profile.save()

    url = iri_to_uri(note.file.url)
    return render(request, 'note.html', {'note': note, 'url': url})


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
