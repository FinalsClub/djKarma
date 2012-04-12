from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json
from django.template import RequestContext
from models import School, Course, Note
from utils import jsonifyModel
from forms import UploadFileForm, SelectTagsForm
from gdocs import convertWithGDocs
from django.http import Http404
from django.contrib.auth.decorators import login_required

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
            return render_to_response('upload.html', {'message': 'Note Successfully Uploaded! Add another!', 'form': form}, context_instance=RequestContext(request))
    #If a note has not been uploaded (GET request), show the upload form.
    else:
        print request.user.username
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form, }, context_instance=RequestContext(request))


def schools(request):
    schools = School.objects.all()
    response = []
    for school in schools:
        response.append((school.pk, school.name))
    return HttpResponse(json.dumps(response), mimetype="application/json")


def search(request):
    tag_form = SelectTagsForm()
    return render_to_response('search.html', {'tag_form': tag_form}, context_instance=RequestContext(request))


def jquery(request):
    tag_form = SelectTagsForm()
    return render_to_response('jqueryTest.html', {'tag_form': tag_form}, context_instance=RequestContext(request))

@login_required
def note(request, note_pk):
    try:
        note = Note.objects.get(pk=note_pk)
    except:
        raise Http404
    return render_to_response('note.html', {'note': note}, context_instance=RequestContext(request))


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
            return render_to_response('notes2.html', {'notes' : notes}, context_instance=RequestContext(request))
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
