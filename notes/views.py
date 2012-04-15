# Standard lib imports
import json
from utils import jsonifyModel
# Django imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms, authenticate, login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
# External lib imports
from gdocs import convertWithGDocs
# Local imports
from models import School, Course, Note
from forms import UploadFileForm, SelectTagsForm

#from django.core import serializers


@login_required
def home(request):
    # If user is authenticated, home view should be upload-notes page
    # Else go to login page

    # If a note has been uploaded (POST request), process it and report success.
    # Return user to upload screen
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            newNote = Note.objects.create(title=form.cleaned_data['title'],
                                course=form.cleaned_data['course'],
                                school=form.cleaned_data['school'],
                                file=request.FILES['note_file'])
            newNote.tags = form.cleaned_data['tags']
            convertWithGDocs(newNote)
            print "upload handled!"
            return render_to_response('upload.html', {'message': 'Note Successfully Uploaded! Add another!', 'form': form})
    #If a note has not been uploaded (GET request), show the upload form.
    else:
        print request.user.username
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form, })


@login_required
def profile(request):
    return render_to_response('profile.html')

# Display user login and signup screens
# the registration/login.html template redirects login attempts
# to django's built-in login view (django.contrib.auth.views.login)
# and user registration is handled by this view (because there is no built-in)
def register(request):
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
            return render_to_response("registration/register.html", {
        'form': form}, context_instance=RequestContext(request))

    form = forms.UserCreationForm()
    return render_to_response("registration/register.html", {
        'form': form}, context_instance=RequestContext(request))


# NOTE: There is currently a css conflict between Twitter Bootstrap and Jquery UI
#       Which prevents the jquery autocomplete from displaying properly.
#       See https://github.com/twitter/bootstrap/issues/156
#       I'll look at fixing this issue shortly
# Handles ajax queries from the School autocomplete form field
def schools(request):
    if request.is_ajax():
        query = request.GET.get('q')
        schools = School.objects.filter(name__contains=query).distinct()
        response = []
        for school in schools:
            response.append((school.pk, school.name))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404

# Handles ajax queries from the Course autocomplete form field
def courses(request):
    if request.is_ajax():
        query = request.GET.get('q')
        courses = Course.objects.filter(title__contains=query).distinct()
        response = []
        for course in courses:
            response.append((course.pk, course.title))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404


def search(request):
    tag_form = SelectTagsForm()
    return render_to_response('search.html', {'tag_form': tag_form})


def jquery(request):
    tag_form = SelectTagsForm()
    return render_to_response('jqueryTest.html', {'tag_form': tag_form})

@login_required
def note(request, note_pk):
    try:
        note = Note.objects.get(pk=note_pk)
    except:
        raise Http404
    return render_to_response('note.html', {'note': note})


def searchByTag(request):
    if request.method == 'POST':
        form = SelectTagsForm(request.POST)
        if form.is_valid():
            response = {}
            tags = form.cleaned_data['tags']
            notes = Note.objects.filter(tags__in=tags).distinct()
            '''
            To fill seth's notes.html template. Got an error so whippped up a quick temp notes2.html
            for n in notes:
                response[n.school.name] = {}
                response[n.school.name][n.course.title] = n
            '''
            return render_to_response('notes2.html', {'notes' : notes})
    raise Http404

def searchBySchool(request):
    response_json = []

    if request.is_ajax():
        schools = School.objects.all()
        for school in schools:
            school_json = jsonifyModel(school, depth=1)
            response_json.append(school_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")

        #A nicer way to do this would be to override the queryset serializer
        #data = serializers.serialize("json", School.objects.all())
        #return HttpResponse(data, mimetype='application/json')
        #json_serializer = serializers.get_serializer("json")()
        #json_serializer.serialize(queryset, ensure_ascii=False, stream=response)


def notesOfSchool(request, school_pk):
    response_json = []
    print 'wtf'
    #if request.is_ajax():
    if 0 == 0:
        #notes = Note.objects.get(school.pk=school_pk)
        school = School.objects.get(pk=school_pk)
        print jsonifyModel(school, depth=2)
        response_json.append(jsonifyModel(school, depth=2))

            #response_json.append(school_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")


def all_notes(request):
    print "using the all_notes view"
    response = {}
    response['schools'] = {}
    for school in School.objects.all():
        print school
        response['schools'][school.name] = {}
        for course in Course.objects.filter(school = school).all():
            print course
            notes = Note.objects.filter(course = course).all()
            response['schools'][school.name][course.title] = notes
    print response
    return render_to_response('notes.html', response)
