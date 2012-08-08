  var file_pk = -1;

  var state = "";
  // Keep track of user's School, Course selection (pks) for 
  // inclusion in final File Upload Form
  var school_pk = "";
  var course_pk = "";

  // School and Course titles for instructions
  var school_name = "None";
  var course_name = "None";

  // After DOM loads
  $(document).ready(function() {
    // Configure AJAX file uploader
    var cancelled = false;
    var uploader = new qq.FileUploader({
        action: ajax_upload_url,
        element: $('#file-uploader')[0],
        multiple: false,
        onCancel: function(id, fileName){
          $('#modal-body-progress').slideUp('fast');
          cancelled = true;
        },
        onSubmit: function(id, fileName){
          // show progress bar
          cancelled = false;
          $('#modal-body-progress').slideDown('fast', function(){
            $('#modal-metadata-form').slideDown('fast');
          });

        },
        onComplete: function(id, fileName, responseJSON) {
          console.log(responseJSON);
            if(responseJSON.success) {
                //alert("success! file_pk: " + responseJSON.file_pk);
                file_pk = responseJSON.file_pk;
            }
        },
        onProgress:function(id, fileName, loaded, total){
          if(!cancelled){
            $('#progress-bar').animate({
                width: String((100*loaded/total)+'%')}, 5000);
            }
        },
        onAllComplete: function(uploads) {
            // uploads is an array of maps
            // the maps look like this: {file: FileObject, response: JSONServerResponse}
            console.log("upload:");
            console.log(uploads);
            //alert("All complete!");
            // Hide file uploader
            
            $('#file-uploader').fadeOut('fast', function(){
              if(!cancelled){
                $('#file-uploader').html("<h2>" + uploads[0].file.name + " uploaded!</h2>");
              }
              $('#file-uploader').fadeIn('fast');
              $('#modal-body-progress').slideUp('fast');

            });
        },
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken',
        },
    });

    // Set jquery Autocomplete on School Search
    $("#modal-school-input").autocomplete({
        source: function(request, response){
            $.ajax({
                url: "/schools",
                data: {'q': request.term },
                success: function(data) {
                    if (data != 'CACHE_MISS')
                    {
                      //console.log(data);
                      
                        response($.map(data, function(item) {
                            return {
                                label: item[1],
                                value: item[1],
                                real_value: item[0]
                            };
                        }));
                    }
                },
                dataType: "json"
            });
        },
        select: function(event, ui) { 
          // ensure suggestion is populated before submit
          $("#modal-school-input").val(ui.item.label);
          // clear course-search-input in case it is populated
          $("#modal-course-input").val("");
          // trigger submit event on auto-complete suggestion
          $("#modal-school-input").submit();  
        },
        minLength: 3
    });
    // End School autocomplete

    $("#modal-school-input").on("submit", function(){
      console.log("school submit");
      enableCourseAutoComplete();
    });
    // any one of the many input fields will trigger
    // the entire form to submit. Prevent this
    $("#modal-metadata-form").on("submit", function(event){
      event.preventDefault();
    });

    $("#modal-meta-submit").on("click", function(){
      if(validateForm()){
        var response = serializeFormData();
        console.log("RESPONSE");
        console.log(response);
      }
    });

  });// end document ready

  // Course autocomplete
  function enableCourseAutoComplete(){
    $("#modal-course-input").autocomplete({
    source: function(request, response){
        $.ajax({
            url: "/courses?school="+school_pk,
            data: {'q': request.term },
            success: function(data) {
                if (data != 'CACHE_MISS')
                {                  
                    response($.map(data, function(item) {
                        return {
                            label: item[1],
                            value: item[1],
                            real_value: item[0]
                        };
                    }));
                }
            },
            dataType: "json"
        });
    },
    select: function(event, ui) { 
      // ensure suggestion is populated before submit
      $("#course-search-input").val(ui.item.label);
      // trigger submit
      $("#course-search-input").submit();  
    },
    minLength: 3
    });
  }

  // Clear form to initial state
  function clearForm(course, school){
    course = typeof course !== 'undefined' ? course : 'None';
    school = typeof school !== 'undefined' ? school : 'None';

    $('#modal-body-progress').hide();
    $('#modal-metadata-form').hide();
    if(course == "None"){
      $("#course-search-input").val("");
      course_pk = "";
      course_name = "None";
    }
    else{
      $("#course-search-input").val(course_name);
      course_pk = course.pk;
      course_name = course.name;
    }

    if(school == "None"){
      $("#school-search-input").val("");
      school_pk = "";
      school_name = "None";
    }
    else{
      $("#school-search-input").val(school_name);
      school_pk = school.pk;
      school_name = school.name;
    }
  }

  function validateForm(){
    message = "Check your ";
    if(school_pk === ""){
      message += " school selection.";
      alert(message);
      return false;
    } else if(course_pk === ""){
      message += " course selection.";
      alert(message);
      return false;
    } else if($('#modal-title-input').val() === ""){
      message += " file title.";
      alert(message);
      return false;
    } else if($('#modal-description-input').val() === ""){
      message += " file description.";
      alert(message);
      return false;
    } else if(file_pk === -1){
      alert("Please upload a file first");
      return false;
    } else if(!$('#modal-tos-agree').is(':checked')){
      alert("Please read and agree to our Terms of Service");
      return false;
    }
    return true;
  }

  function serializeFormData(){
    response = new Object();
    response.school = school_pk;
    response.course = course_pk;
    response.title = $('#modal-title-input').val();
    response.description = $('#modal-description-input').val();
    response.type = $('input[name=optionsRadio]:checked').val();
    response.file = file_pk;
    console.log('RESPONSE');
    console.log(response);
    return response;

  }