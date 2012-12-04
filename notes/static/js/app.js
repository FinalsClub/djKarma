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

  // Search results
  var slide_out = {'direction': 'left', 'mode': 'hide'};
  var slide_in = {'direction': 'right', 'mode': 'show'};

  $(".filter_button").click(function() {
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
    console.log("course selected");
    // fill the lightbox_instructyion with the chosen course's title
    $('#lightbox_upload_course_sidebar').text($(this).text());
    // hide the my courses button
    $(".select_box").effect("slide", slide_out, 500);
    //$('#button_my_course').hide();
    // TODO: register handler for clicking mycourses reshow the my courses button
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

  $("#submit-lightbox-upload").click( function() {
    $.ajax({
      url: '/filemeta',
      data: load_upload_data(),
      success: function(data){
        if(data.status === 'success'){
          console.log('success');
          $('#lightbox_add_note').hide();

        }
        else{
          alert(data.message);
        }
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
