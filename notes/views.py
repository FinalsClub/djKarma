from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json
from django.template import RequestContext
from models import School, Course, Note
from utils import jsonifyModel
from forms import UploadFileForm
from gdocs import convertWithGDocs
from django.http import Http404

#from django.core import serializers


def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            newNote = Note.objects.create(title=request.POST['title'],
                                course= Course.objects.get(pk=request.POST['course']),
                                school = School.objects.get(pk=request.POST['school']),
                                file=request.FILES['note_file'])
            convertWithGDocs(newNote)
            print "upload handled!"
            return render_to_response('index.html', {'message': 'Note Successfully Uploaded! Add another!', 'form': form}, context_instance=RequestContext(request))
    else:
        form = UploadFileForm()
    return render_to_response('index.html', {'form': form}, context_instance=RequestContext(request))


def note(request, note_pk):
    try:
        note = Note.objects.get(pk=note_pk)
    except:
        raise Http404
    return render_to_response('note.html', {'note': note}, context_instance=RequestContext(request))

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
    response = {}
    for school in School.objects.all():
        response[school.name] = {}
        for course in Course.objects.filter(school=school).all():
            notes = Note.objects.filter(course=course).all()
            response[school.name][course.title] = notes
    return render_to_response('notes.html', response)
