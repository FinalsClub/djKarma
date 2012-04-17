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

# Standard lib imports
import json
from utils import jsonifyModel
# Django imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms, authenticate, login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
# External lib imports
from gdocs import convertWithGDocs
# Local imports
from models import School, Course, Note
from forms import UploadFileForm, SelectTagsForm

#from django.core import serializers


# Landing Page
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
            try:
                convertWithGDocs(newNote)
            except:
                newNote.delete()
                return render(request, 'upload.html', {'message': 'We\'re having trouble working with your file. Please ensure it has a file extension (i.e .doc, .rtf)', 'form': form})

            return render(request, 'upload.html', {'message': 'Note Successfully Uploaded! Add another!', 'form': form})
    #If a note has not been uploaded (GET request), show the upload form.
    else:
        print request.user.username
        # Provide bogus default school and course data to ensure
        # legitimate data is chosen
        form = UploadFileForm(initial={'course': -1, 'school': -1})
    return render(request, 'upload.html', {'form': form, })

# User Profile
@login_required
def profile(request):
    return render(request, 'profile.html')


# Display user login and signup screens
# the registration/login.html template redirects login attempts
# to django's built-in login view (django.contrib.auth.views.login).
# new user registration is handled by this view (because there is no built-in)
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
            return render(request, "registration/register.html", {
        'form': form})
    else:
        form = forms.UserCreationForm()
        return render(request, "registration/register.html", {'form': form})


# Ajax: School autcomplete form field
def schools(request):
    if request.is_ajax():
        query = request.GET.get('q')
        schools = School.objects.filter(name__contains=query).distinct()
        response = []
        for school in schools:
            response.append((school.pk, school.name))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404


# Ajax: Course autocomplete form field
def courses(request):
    if request.is_ajax():
        query = request.GET.get('q')
        courses = Course.objects.filter(title__contains=query).distinct()
        response = []
        for course in courses:
            response.append((course.pk, course.title))
        return HttpResponse(json.dumps(response), mimetype="application/json")

    raise Http404


# Browse and Search Notes
def search(request):
    # If the SelectTagsForm form has been submitted, display search result
    if request.method == 'POST':
        tag_form = SelectTagsForm(request.POST)
        if tag_form.is_valid():
            tags = tag_form.cleaned_data['tags']
            notes = Note.objects.filter(tags__in=tags).distinct()
            return render(request, 'notes2.html', {'notes': notes})
        else:
            return render(request, 'search.html', {'tag_form': tag_form})

    # If this is a GET request, display the SelectTagsForm
    else:
        tag_form = SelectTagsForm()
        return render(request, 'search.html', {'tag_form': tag_form})


# View Note HTML
@login_required
def note(request, note_pk):
    try:
        note = Note.objects.get(pk=note_pk)
    except:
        raise Http404
    return render(request, 'note.html', {'note': note})


# Ajax: Return all schools and courses in JSON
# Used by search page javascript
def searchBySchool(request):
    response_json = []

    if request.is_ajax():
        schools = School.objects.all()
        for school in schools:
            school_json = jsonifyModel(school, depth=1)
            response_json.append(school_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")
    else:
        raise Http404

        #A nicer way to do this would be to override the queryset serializer
        #data = serializers.serialize("json", School.objects.all())
        #return HttpResponse(data, mimetype='application/json')
        #json_serializer = serializers.get_serializer("json")()
        #json_serializer.serialize(queryset, ensure_ascii=False, stream=response)

# Ajax: Return all notes belonging to a school
# Used by search page javascript
def notesOfSchool(request, school_pk):
    response_json = []
    print 'wtf'
    if request.is_ajax():
        #notes = Note.objects.get(school.pk=school_pk)
        school = School.objects.get(pk=school_pk)
        print jsonifyModel(school, depth=2)
        response_json.append(jsonifyModel(school, depth=2))

            #response_json.append(school_json)
        return HttpResponse(json.dumps(response_json), mimetype="application/json")
    else:
        raise Http404

# Display all notes
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
