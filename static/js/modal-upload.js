  var file_pk = -1;
  var file_url = "";

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

    // Assumes variable csrf_token is available
    // in embedding document
    setupAjax();
    //.doc, .docx, .pdf, .rtf, and .txt file
    // Configure AJAX file uploader
    var cancelled = false;
    var uploader = new qq.FileUploader({
        action: ajax_upload_url,
        element: $('#file-uploader')[0],
        allowedExtensions: ['doc', 'docx', 'pdf' ,'txt', 'rtf'],
        sizeLimit: 2097152,
        multiple: false,
        onCancel: function(id, fileName){
          // hide progress bar and show upload button
          $('#modal-body-progress').slideUp('fast', function(){
            $('.qq-upload-button').slideDown('fast');
          });
          cancelled = true;
        },
        onSubmit: function(id, fileName){
          
          cancelled = false;
          // hide upload button and show progress bar
          $('.qq-upload-button').slideUp('fast', function(){
            $('#modal-body-progress').slideDown('fast');
            $('#modal-metadata-form').slideDown('fast');
          });
        },
        onComplete: function(id, fileName, responseJSON) {
          console.log(responseJSON);
            if(responseJSON.success) {
                //alert("success! file_pk: " + responseJSON.file_pk);
                file_pk = responseJSON.file_pk;
                file_url = responseJSON.file_url;
                //$('#new-file-link').attr('href',file_url);

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
            if(!cancelled){
              $('#file-uploader').slideUp('fast', function(){
                $('#file-uploader-label').html("<h2>" + uploads[0].file.name + " uploaded!</h2>").slideDown('fast');
                //$('#file-uploader').html("<h2>" + uploads[0].file.name + " uploaded!</h2>");
              //$('#file-uploader').fadeIn('fast');
              $('#modal-body-progress').slideUp('fast');

              });
            }
            else{
              $('#modal-body-progress').slideUp('fast');
            }
            
        },
        params: {
            'csrf_token': csrf_token,
            'csrf_name': 'csrfmiddlewaretoken',
            'csrf_xname': 'X-CSRFToken'
        }
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
    }); // End School autocomplete

    // School submit
    $("#modal-school-form").on("submit", function(event){
      event.preventDefault();
      console.log("school submit: " + $('#modal-school-input').val());
      //form_data = $(this).serializeArray();
      $.ajax({
          url: "/smartModelQuery",
          data: {'title': $('#modal-school-input').val(),
                'type': 'school'},
          success: function(data){
            $('#modal-course-input').val('');
            course_pk = -1;
            course_name = '';
            smartModelQueryResponseHandler(data);
          },
          type: 'POST'
      });
    });

    // Course submit
    $("#modal-course-form").on("submit", function(event){
      event.preventDefault();
      console.log("course submit: " + $('#modal-course-input').val());
      //form_data = $(this).serializeArray();
      $.ajax({
          url: "/smartModelQuery",
          data: {'title': $('#modal-course-input').val(),
                'type': 'course',
                'school': school_pk},
          success: function(data){
            smartModelQueryResponseHandler(data);
          },
          type: 'POST'
      });
    });
    // hitting enter in any one of the many input fields will trigger
    // the entire form to submit. Prevent this
    //$("#modal-metadata-form").on("submit", function(event){
    //  event.preventDefault();
    //});

    // file meta data submit
    $("#modal-meta-submit").on("click", function(){
      if(validateForm()){
        var response = serializeFormData();
        $.ajax({
          url: '/filemeta',
          data: response,
          success: function(data){
            if(data.status === 'success'){
              // TODO: put thank you message and clear form here
              $('#modal-upload-button').hide();
              showUploadSuccessMessage(data);
              $('#modal-metadata-form').slideUp('slow');
            }
            else{
              alert('Please check your form input');
            }
          },
          type: 'POST'
        });
      }
    });

    // Add school click handler
    $('#school-suggestions').on('click', '#modal-add-school', function(){
      //setupAjax();
      console.log("add school");
      type = 'school';
      $.ajax({
          url: '/add',
          data: {'title': $('#modal-school-input').val(), 'type': type},
          success: function(data){
            if(data.status === 'success'){
              if(data.type === 'school'){
                school_pk = data.new_pk;
                $('#school-suggestions').slideUp('fast');
                $('#modal-course').slideDown('fast');
              }
            }
          },
          type: 'POST'
      });
    });

    // select a school from /smartModelQuery suggestions
    $('#school-suggestions').on('click', '.school-suggestion', function(){
      console.log("suggest " + $(this).attr('id') + ": " + $(this).html());
      school_pk = $(this).attr('id');
      school_name = $(this).html();
      $('#school-suggestions').slideUp('fast');
      $('#modal-school-input').val(school_name);
      enableCourseAutoComplete();
      $('#modal-course').slideDown('fast');
    });

    // create new course request
    $('#course-suggestions').on('click', '#modal-add-course', function(){
      //setupAjax();
      console.log("add course");
      type = 'course';
      $.ajax({
          url: '/add',
          data: {'title': $('#modal-course-input').val(), 'type': type},
          success: function(data){
            if(data.status === 'success'){
              if(data.type === 'course'){
                course_pk = data.new_pk;
                $('#course-suggestions').slideUp('fast');
                $('#modal-misc').slideDown('fast');
              }
            }
          },
          type: 'POST'
      });
    });

    // select a course from /smartModelQuery suggestions
    $('#course-suggestions').on('click', '.course-suggestion', function(){
      console.log("suggest " + $(this).attr('id'));
      course_pk = $(this).attr('id');
      course_name = $(this).html();
      $('#course-suggestions').slideUp('fast');
      $('#modal-course-input').val(course_name);
      $('#modal-misc').slideDown('fast');
    });

    // upload again button handler
     $('#modal-upload-again-button').on('click', function(){
        course = {};
        school = {};
        school.pk = school_pk;
        school.name = school_name;
        course.pk = course_pk;
        course.name = course_name;
        clearForm(course, school);
     });

  });// end document ready

  function showUploadSuccessMessage(data){
    message = "You just uploaded <a href=\""+file_url+"\">" + $('#modal-title-input').val() + "</a> to " + $('#modal-course-input').val() + " at " + $('#modal-school-input').val() + ".<br/>" +
              "You've been awarded <span class=\"karma\">+" + data.karma + " </span> karma points for your contribution.";
    $('#upload-success-message').html(message);
    animate_karma(data.karma);
    $('#modal-upload-success').show();

  }

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
      $('#modal-course-input').val(ui.item.label).submit();
    },
    minLength: 3
    });
  }

  // Clear form to initial state
  function clearForm(course, school){
    course = typeof course !== 'undefined' ? course : 'None';
    school = typeof school !== 'undefined' ? school : 'None';
    var file_pk = -1; // reset file paramters to avoid resubmission
    var file_url = "";
    $('.qq-upload-button').show(); // Click / Drag to upload btn
    $('.qq-upload-drop-area').hide(); // Drop area that appears when file dragged into browser
    $('#modal-upload-button').show(); // finish upload btn
    $('#modal-upload-success').hide(); // div containing upload again btn and link to note
    $('.qq-upload-list').html(''); // list of uploaded files, filesize and % uploaded
    $('#file-uploader').show(); // the root div containing the file uploader
    $('#file-uploader-label').hide(); // '<filename> uploaded!'
    $('#modal-body-progress').hide(); // parent div of progress bar
    $('#modal-metadata-form').hide(); // entire form but file uploader
    $('#modal-course').hide(); // course selector div
    $('#course-suggestions').hide(); // course suggestions within modal-course
    $('#school-suggestions').hide(); // school suggestions within modal-school
    $('#modal-misc').hide(); // file metadata parent div: title, type, desc
    $('#modal-title-input').val(""); // title input field
    $('#modal-description-input').val(""); // desc input field
    if(course == "None"){
      $("#modal-course-input").val("");
      course_pk = "";
      course_name = "None";
    }
    else{
      course_pk = course.pk;
      course_name = course.name;
      $("#modal-course-input").val(course_name);
      $('#modal-course').show();
    }

    if(school == "None"){
      $("#modal-school-input").val("");
      school_pk = "";
      school_name = "None";
    }
    else{
      school_pk = school.pk;
      school_name = school.name;
      $("#modal-school-input").val(school_name);
      $('#modal-metadata-form').show();
    }

    if(course !== "None" && school !== "None")
      $('#modal-misc').show();
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
    }
    return true;
  }

  function serializeFormData(){
    response = new Object();
    response.school_pk = school_pk;
    response.course_pk = course_pk;
    response.title = $('#modal-title-input').val();
    response.description = $('#modal-description-input').val();
    response.type = $('input[name=optionsRadio]:checked').val();
    //javascript booleans are 'true', 'false'. python's are 'True', 'False'
    if($('#modal-current-course').is(':checked'))
      response.in_course = 'True';
    else
      response.in_course = 'False';

    response.file_pk = file_pk;
    console.log('RESPONSE');
    console.log(response);
    return response;

  }

  // Handles response from /smartModelQuery
  function smartModelQueryResponseHandler(data){
    // A model matching query was found
    if(data.status == 'success'){
      console.log('model found!');
      if(data.type == 'school'){
        school_pk = data.model_pk;
        school_name = data.model_name;
        enableCourseAutoComplete();
        $('#school-suggestions').slideUp('fast', function(){
          $('#modal-course').slideDown('fast');
        });
      }
      else if(data.type == 'course'){
        course_pk = data.model_pk;
        course_name = data.model_name;
        $('#course-suggestions').slideUp('fast', function(){
          $('#modal-misc').slideDown('fast');
        });
      }
    }
    // No model matching query found. Present create form
    else if(data.status == 'suggestion'){
      console.log("no model found for type: " + data.type);
      if(data.type == "school"){
        injectSchoolSuggestions(data);
      }
      else if(data.type == "course"){
        injectCourseSuggestions(data);
      }
    }
    else if(data.status == 'no_match'){
      if(data.type == "school"){
        html = "<p><strong>School not found.</strong><a id=\"modal-add-school\" class=\"button\">Add \""+ $('#modal-school-input').val()+ "\"</a></p>";
        $('#school-suggestions').html(html).slideDown('fast');
      }
      else if(data.type == "course"){
        html = "<p><strong>Course not found.</strong><a id=\"modal-add-course\" class=\"button\">Add \""+ $('#modal-course-input').val()+ "\"</a></p>";
        $('#course-suggestions').html(html).slideDown('fast');
      }
    }
  }

  // Injects school suggestion json response
  // called by smartModelQuery()
  function injectSchoolSuggestions(data){
    console.log("inject school suggestions");
    console.log(data);
    html = "<p><strong>School not found.</strong> Is it one of these?</p>"+
            "  <ul>";

    $.each(data.suggestions, function(index, school){
      html += "<li><a href\"#\" class=\"school-suggestion\" id=\""+school.pk+"\" href=\"#\">"+ school.name +"</a></li>";
    });


    html += "  </ul>"+
            "  <p>Not there? <a id=\"modal-add-school\" class=\"button\">Add \""+ $('#modal-school-input').val()+ "\"</a></p>";
    $('#school-suggestions').html(html).slideDown('fast');
  }

  // Injects course suggestion json response
  // called by smartModelQuery()
  function injectCourseSuggestions(data){
    console.log("inject course suggestions");
    html = "<p><strong>Course not found.</strong> Is it one of these?:</p>"+
            "  <ul>";

    $.each(data.suggestions, function(index, course){
      html += "<li><a class=\"course-suggestion\" id=\""+course.pk+"\" href=\"#\">"+ course.title +"</a></li>";
    });


    html += "  </ul>"+
            "  <p>Not there? <a id=\"modal-add-course\" class=\"button\">Add \""+ $('#modal-course-input').val()+ "\"</a></p>";
    $('#course-suggestions').show();
    //console.log("select course-suggestions: " + $('#course-suggestions').attr('id'));
    $('#course-suggestions').html(html).slideDown('fast');
    //sanity testing
    console.log("sanity test");
    $('#course-suggestions').show();
  }

  // set appropriate headers
  // to comply with Django
  // CSRF-Protection
  function setupAjax(){
    // Assumes variable csrf_token is made available
    // by embedding document
    $.ajaxSetup({
          beforeSend: function(xhr, settings) {
              if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                  // Only send the token to relative URLs i.e. locally.
                  xhr.setRequestHeader("X-CSRFToken", csrf_token);
              }
          }
    });
  }
