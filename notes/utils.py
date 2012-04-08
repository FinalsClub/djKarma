from models import School, Course, Note

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
    elif isinstance(model, Note):
        json_result["_id"] = model.pk
        json_result["notedesc"] = model.title
    return json_result
