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
    $(".results_container").effect("slide", slide_out, 1000);
    $(".button_interior").removeClass("button_interior);
    $($(this).data('target')).effect("slide", slide_in, 1000);
    $(this).addClass("button_interior);

  });



});
