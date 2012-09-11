$(document).ready(function() {
    var school_pk = "0";

    // Course submit
    $("#modal-addcourse-form").on("submit", function(event){
      event.preventDefault();
      console.log("course submit: " + $('#modal-addcourse-input').val());
      //form_data = $(this).serializeArray();
      $.ajax({
          url: "/smartModelQuery",
          data: {'title': $('#modal-course-input').val(),
                'type': 'course'},
          success: function(data){
            smartModelQueryResponseHandler(data);
          },
          type: 'POST'
      });
    });

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

    function enableCourseAutoComplete(){
      $("#modal-addcourse-input").autocomplete({
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
        $('#modal-addcourse-input').val(ui.item.label).submit();
      },
      minLength: 3
      });
    }

    // Injects course suggestion json response
    // called by smartModelQuery()
    function injectCourseSuggestions(data){
      console.log("inject course suggestions");
      html = "<p><strong>Course not found.</strong> Is it one of these?:</p>"+
              "  <ul>";

      $.each(data.suggestions, function(index, course){
        html += "<li><a class=\"course-suggestion\" id=\""+course.pk+"\" href=\"#\">"+ course.name +"</a></li>";
      });


      html += "  </ul>"+
              "  <p>Not there? <a href\"#\" id=\"modal-add-course\" class=\"button\">Add \""+ $('#modal-course-input').val()+ "\"</a></p>";
      $('#course-add-suggestions').html(html).slideDown('fast');
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
          $('#course-add-suggestions').slideUp('fast', function(){
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
          $('#course-add-suggestions').html(html).slideDown('fast');
        }
      }
    }

    setupAjax();
    enableCourseAutoComplete();
});
