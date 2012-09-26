var edit_course_element;

$(document).ready(function() {
  // note: we're re-using the .file-actions class bc all
  // action widgets should appear identical. we should rename the
  // css class to something generic like action-widgets etc.
  edit_course_element = $('#course-actions').find('.edit-course');

  $('.edit-course').click(function(event){editCourseClickListener(event);});

  // If the user got to this page by clicking
  // an 'edit' widget on a course row, editing == true
  if(editing_course === true){
    editing_course = false;
    $('.edit-course').click();
  }
    
}); // end on document ready

// handle clicks to the .edit-course widget
function editCourseClickListener(event){
  // the edit widget directs to course.get_absolute_url()/edit
  // On this page, ignore the href link
  event.preventDefault();
  editing_course = !editing_course;
    if(editing_course === true){
      console.log('edit course. ');
      edit_course_element.html(edit_course_element.html().replace("Edit","Done"));
      $('#course-title').hide();
      $('#course-title-editable-input').val(view_course_title);
      $('#course-title-editable').show();
      $('#course-professor').hide();
      $('#course-professor-editable-input').val(view_course_professor);
      $('#course-professor-editable').show();
    }
    else{
      console.log('submit course edits');
      validateAndSubmitCourseMeta();
      edit_course_element.html(edit_course_element.html().replace("Done","Edit"));
      $('#course-title').show();
      $('#course-title-editable').hide();
      $('#course-professor').show();
      $('#course-professor-editable').hide();
    }

}

// Resize the iframe upon html injection
// Note: IE6 does not support contentWindow
// Test this case
function autoResize(id){
    var newheight;
    var newwidth;

    if(document.getElementById){
      newheight=document.getElementById(id).contentWindow.document .body.scrollHeight;
      newwidth=document.getElementById(id).contentWindow.document .body.scrollWidth;
    }

    document.getElementById(id).height = (newheight) + "px";
    //document.getElementById(id).width= (newwidth) + "px";
    //alert('height: ' + newheight);
}

// Validate course meta input fields and send request
function validateAndSubmitCourseMeta(){
    do_submit = false;
    metaData = {'course_pk': view_course_pk};
    title_input = $.trim($('#course-title-editable-input').val());
    professor_input = $.trim($('#course-professor-editable-input').val());
    //console.log(professor_input);
    //console.log(view_course_professor);
    if(title_input !== "" && title_input !== view_course_title){
      metaData.title = $.trim($('#course-title-editable-input').val());
      do_submit = true;
    }
    if(professor_input !== "" && professor_input !== view_course_professor){
      metaData.professor = $.trim($('#course-professor-editable-input').val());
      do_submit = true;
    }
    if(do_submit){
      console.log('/editCourseMeta request');
      console.log(metaData);
      $.ajax({
        url: "/editCourseMeta",
        type: 'POST',
        data: metaData,
        success: function(data) {
            if(data.status === "success"){
              console.log("successfully edited course meta");
              reflectNewCourseMeta(data);
            }
        },
        dataType: "json"
      }); // end ajax
    } // end if(do_submit)
}

// Update the script and html state to reflect new course attributes
// Called from processAndSubmitCourseMeta on successful POST
function reflectNewCourseMeta(data){
  if('title' in data){
    view_course_title = data.title;
    $('#course-title').html(view_course_title);
  }
  if('professor' in data){
    view_course_professor = data.professor;
    $('#course-professor').html(view_course_professor);
  }

}