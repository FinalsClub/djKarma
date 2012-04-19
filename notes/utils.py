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

from models import School, Course, File

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
            for course in model.course_set.all():
                course_json = jsonifyModel(course, depth - 1)
                json_result["courses"].append(course_json)
    elif isinstance(model, Course):
        json_result["_id"] = model.pk
        json_result["title"] = model.title
        json_result["notes"] = []
        if(depth > 0):
            for note in model.note_set.all():
                note_json = jsonifyModel(note)
                json_result["notes"].append(note_json)
    elif isinstance(model, File):
        json_result["_id"] = model.pk
        json_result["notedesc"] = model.title
    return json_result
