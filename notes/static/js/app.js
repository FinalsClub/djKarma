$(document).ready(function(){

// Click Handlers
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

  // Search results
  var slide_out = {'direction': 'left', 'mode': 'hide'};
  var slide_in = {'direction': 'left', 'mode': 'show'};

  $(".filter_button").click(function() {
    // Slide out the current content
    $(".results_container").effect("slide", slide_out, 500);
    // Slide in the new content
    $($(this).data('target')).effect("slide", slide_in, 500);
    // remove the current active button
    $(".filter_button.button_interior").parent().removeClass("button_bevel");
    $(".filter_button.button_interior").removeClass("button_interior");
    // activate the clicked button
    $(this).parent().addClass("button_bevel");
    $(this).addClass("button_interior");
  });

  // Join a course to your profile
  $(".course_meta_action.course_meta_join").on("click", function(){
    //var response = serializeCourseFormData();
    $.ajax({
      url: '/add-course',
      data: {'id': $(this).data('id')},
      context: this,
      success: function(data){
        // put callback here to clear form and tell of success
        if(data.status === 'success'){
          console.log("added course to profile");
          $(this).removeClass('course_meta_join');
          $(this).addClass('course_meta_drop');
          $(this).text('drop');
        }
      },
      type: 'POST'
  });
  });

  // Drop a course from your profile
  $(".course_meta_action.course_meta_drop").on("click", function(){
    //var response = serializeCourseFormData();
    $.ajax({
      url: '/drop-course',
      data: {'id': $(this).data('id')},
      context: this,
      success: function(data){
        // put callback here to clear form and tell of success
        if(data.status === 'success'){
          console.log("dropped course from profile");
          console.log($(this));
          $(this).removeClass('course_meta_drop');
          $(this).addClass('course_meta_join');
          $(this).text('join');
        }
      },
      type: 'POST'
  });
  });

  $('.class_select').click( function() {
    course_pk = $(this).data('id');
    console.log("course selected");
  });

  function load_upload_data(){
    var upload_data = {};
    upload_data.school_pk = school_pk;
    upload_data.course_pk = course_pk;
    upload_data.file_pk = file_pk;
    upload_data.title = $("#add_note_title_txt").val();
    upload_data.description = $("#add_note_description_txt").val();
    console.log(upload_data);
    return upload_data;
  }

  $("#modal_upload_button").click( function() {
    var res = load_upload_data();
    $.ajax({
      url: '/filemeta',
      data: res,
      success: function(data){
        if(data.status === 'success'){
          console.log('success');
        }
        else{
          alert(data.message);
        }
      },
      type: 'POST'
    });
    
  });


});
