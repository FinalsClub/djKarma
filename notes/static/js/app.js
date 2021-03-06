$(document).ready(function(){

  // Click Handlers
  // Dismiss cover and play video
  $("#home_video_overlay").click(function(){
    $(this).hide();
  });

  // Toggle: Login box dropdown
  $("span#login_toggle").click(function(){
    $("#login_box").toggle();
  });

  //
  $("#global_header_add_course").click(function(){
    $("#lightbox_choose_course").show();
  });

  // Choose school click handlers, show and submit
  $("#choose_school").click(function(){
    $("#lightbox_choose_school").show();
  });
  $("a#submit-lightbox-choose-school").click(function() {
    $("form#choose_school_form").submit();
    $("#lightbox_choose_school").hide();
    // TODO: clear this form after hiding it
  });

  // Search and join a course handlers
  $("a.add_course").click(function(){
    $("#lightbox_choose_course").show();
  });

  $("#submit-lightbox-choose-course").click(function(){
    //$("form#choose_course_form").submit();
    console.log("submitting lightbox choose course");
    $.ajax({
      url: '/add-course',
      data: {'title': $("#id_course").val() },
      success: function(data) {
        console.log("added course");
        console.log(data);
        $('#added_course_list').append('<p>added: '+ data['title'] +'</p>');
        $("#id_course").val('');
      },
      type: 'POST'
    });
  // If the course can't be found, show the option to create course
  // This js logic lives in n_lightbox_choose_course

  });

  $('a.create_course_link').click(function(){
    // dismisses choose course lightbox and shows create course

    $("#lightbox_choose_course").hide();
    $("#lightbox_create_course").show();
    // copy course name from the choose course form to create course form
    $("#id_title").val($("#id_course").val());
  });

  $('a.create_school_link').click(function(){
    // dismisses choose school lightbox and shows create school

    $("#lightbox_choose_school").hide();
    $("#lightbox_create_school").show();
    // copy school name from the choose school form to create school form
    $("#id_title").val($("#id_school").val());
  });

  // Toggle: my courses dropdown
  $("#global_header_mycourses_copy").click(function(){
    $("#global_header_mycourses_list").toggle();
    $("#global_header_add_course").toggle();
  });

  // Toggle: avatar menu dropdown
  $("#global_header_avatar_menu").click(function(){
    $("#global_header_avatar_moreinfo").toggle();
  });

  // Show Signup lightbox
  $("#login_signup").click(function() {
    $("#lightbox_signup").toggle();
  });

  // Show Add Note lightbox
  $("#global_header_addnote").click(function() {
    if (typeof course_title != 'undefined'){
      $("#lightbox_upload_course_sidebar").text(course_title);
    }
    $("#lightbox_add_note").toggle();
  });

  // Dismiss all lightboxes
  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });

  // Submit login form
  $("#login_submit").click(function() {
    $("form#login_form").submit();
  });

  // Display course select box
  $(".show_select").click(function(){
    $($(this).data('target')).show()
  });

  // setup the lightbox_add_note#datepicker created_on jqueryui datepicker
  $( "#datepicker" ).datepicker();

  function vote_thank(e) {
    console.log("vote_thank:"+vote_state);
    $.ajax({
      url: "/vote/"+$(e).data("id"),
      data: {'vote': 1},
      type: "POST",
      context: e,
      success: function(){
        console.log("vote_null:"+vote_state);
        $(e).hide();
        $(".flag").hide();
        $("span#thanked_or_flagged").text("thanked");
        $(".voted_message").show();
      }
    });
  }

  function vote_flag(e) {
    console.log("vote_flag:"+vote_state);
    $.ajax({
      url: "/vote/"+$(e).data("id"),
      data: {'vote': -1},
      type: "POST",
      context: e,
      success: function(){
        console.log("vote_null:"+vote_state);
        $(e).hide();
        $(".thank").hide();
        $("span#thanked_or_flagged").text("flagged");
        $(".voted_message").show();
      }
    });
  }

  function vote_null(e) {
    console.log("vote_null:"+vote_state);
    $.ajax({
      url: "/vote/"+$(e).data("id"),
      data: {'vote': 0},
      type: "POST",
      context: e,
      success: function(){
        $(e).hide();
        $(".flag").show();
        $(".thank").show();
      }
    });
  }

  // register vote click handlers
  $(".voted_message").click(function(){vote_null(this)})
  $(".flag").click(function(){vote_flag(this)})
  $(".thank").click(function(){vote_thank(this)})
 

  // Search results
  var slide_out = {'direction': 'left', 'mode': 'hide'};
  var slide_in = {'direction': 'right', 'mode': 'show'};

  $(".filter_button").click(function() {
    if( browse === false ) {
      // Slide out the current content
      $(".results_container").effect("slide", slide_out, 300);
      // Slide in the new content
      $($(this).data('target')).effect("slide", slide_in, 300);
      // remove the current active button
      $(".filter_button.button_interior").parent().removeClass("button_bevel");
      $(".filter_button.button_interior").removeClass("button_interior");
      // activate the clicked button
      $(this).parent().addClass("button_bevel");
      $(this).addClass("button_interior");
    } else {
      window.location = $(this).data('url');
    }
  });

  // Join a course to your profile
  function addCourse(e){
    //var response = serializeCourseFormData();
    $.ajax({
      url: '/add-course',
      data: {'id': $(e).data('id')},
      context: e,
      success: function(data){
        // put callback here to clear form and tell of success
        if(data.status === 'success'){
          $(e).removeClass('course_meta_join');
          $(e).addClass('course_meta_drop');
          $(e).text('drop');
          // resetting button to drop the added course without refreshing
          $(e).on("click", function(){dropCourse(e)});
        }
      },
      type: 'POST'
    });
  }

  // Drop a course from your profile
  function dropCourse(e){
    //var response = serializeCourseFormData();
    $.ajax({
      url: '/drop-course',
      data: {'id': $(e).data('id')},
      context: e,
      success: function(data){
        // put callback here to clear form and tell of success
        if(data.status === 'success'){
          $(e).removeClass('course_meta_drop');
          $(e).addClass('course_meta_join');
          $(e).text('join');
          // reset handler to re-add course
          $(e).on("click", function(){addCourse(e)});
        }
      },
      type: 'POST'
    });
  }

  // set join/drop handlers
  $(".course_meta_action.course_meta_join").click(function(){addCourse(this)});
  $(".course_meta_action.course_meta_drop").click(function(){dropCourse(this)});


/* Upload functions */
// TODO: split off into upload.js

  // Choose a course, hide the select field
  $('.course-select').click( function() {
    course_pk = $(this).data('id');
    // fill the lightbox_instruction with the chosen course's title
    $('#lightbox_upload_course_sidebar').text($(this).text());
    // hide the my courses drop down
    $(".select_box").effect("slide", slide_out, 200);
  });

  function load_upload_data(){
    var upload_data = {};
    upload_data.school_pk = school_pk;
    upload_data.course_pk = course_pk;
    upload_data.file_pk = file_pk;
    upload_data.title = $("#add_note_title_txt").val();
    upload_data.description = $("#add_note_description_txt").val();
    // TODO: make this default to {{ today }} if empty
    upload_data.created_on = $("#datepicker").val();
    console.log(upload_data);
    return upload_data;
  }

  function load_course_data(){
    var course_data = {};
    course_data.title = $('#id_title').val();
    course_data.field = $('#id_field').val()
    course_data.instructor_email = $('#id_instructor_email').val();
    course_data.instructor_name = $('#id_instructor_name').val();
    course_data.desc = $('#id_desc').val();
    return course_data;
  }


  $("#submit-lightbox-upload").click( function() {
    $.ajax({
      url: '/filemeta',
      data: load_upload_data(),
      success: function(data){
        if(data.status === 'success'){
          console.log('success');
          $('#lightbox_add_note').hide();
          document.location.reload(true);
        }
        else{
          alert(data.message);
        }
      },
      type: 'POST'
    });

  });

  $("#submit-lightbox-create-school").click(function() {
    $.ajax({
      url: '/schools',
      data: { 'school_id': acc_school_id },
      success: function(data){
        // TODO: add the course to my courses list and on dashboard
        $('#lightbox_create_school').hide();
        document.location.reload(true);
      },
      type: 'POST'
    });
  });

  $("#submit-lightbox-create-course").click(function() {
    $.ajax({
      url: '/create-course',
      data: load_course_data(),
      success: function(data){
        // TODO: add the course to my courses list and on dashboard
        $('#lightbox_create_course').hide();
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

  setupAjax();


});
