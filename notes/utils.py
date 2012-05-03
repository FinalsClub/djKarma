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

from models import School, Course, File, Tag
from forms import UploadFileForm
from django import forms as djangoforms
from simple_autocomplete.widgets import AutoCompleteWidget
from django.template.defaultfilters import slugify

# Returns a python dictionary representation of a model
# The resulting model is ready for json.dumps()
# model is a Django Model
# depth is how many levels of foreignKey introspection should be performed
# jsonifyModel(School, 1) returns school json at course detail
# jsonifyModel(School, 2) returns school json at note detail


def jsonifyModel(model, depth=0):
    json_result = {}
    if isinstance(model, School):
        json_result["_id"] = model.pk
        json_result["name"] = model.name
        json_result["courses"] = []
        if(depth > 0):
            for course in model.course_set.all().order_by('title'):
                course_json = jsonifyModel(course, depth - 1)
                json_result["courses"].append(course_json)
    elif isinstance(model, Course):
        json_result["_id"] = model.pk
        json_result["title"] = model.title
        json_result["notes"] = []
        if(depth > 0):
            for note in model.file_set.all().order_by('-timestamp'):
                note_json = jsonifyModel(note)
                json_result["notes"].append(note_json)
    elif isinstance(model, File):
        json_result["_id"] = model.pk
        json_result["notedesc"] = model.title
    return json_result


# file: a File object , csvString: a csv string of Tags
# Retrieve or Create a tag corresponding to each string
# and assign it to file

def processCsvTags(file, csvString):
    if not isinstance(file, File):
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


# Creates an UploadFileForm and pre-populates the school field
# With the uer's school, if available


def uploadForm(user):
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
