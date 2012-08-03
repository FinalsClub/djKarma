// Handles search form submission and ajax result receiving
// depends on user_pk being provided by the embedding page

    // Handle search request from navbar search
    $('.nav-collapse').on("submit", ".navbar-search", function(event){
      event.preventDefault(); // ensure no DOM handling
      console.log("SEARCH INTERCEPT");
      ajaxSearchQuery($('#navbar-search-input').val(), search_callback);
      return false; // do not pass event on to DOM handler
    });

  // handle search response
  var search_callback = function(data){
    console.log(data);
    $('#search-results').fadeOut('fast', function(){
      $('#search-results').html(data).fadeIn('fast');
    });
  
  };

  // perform ajax /search query
  function ajaxSearchQuery(query, callback){
    $.ajax({
      url: "/search",
      data: {'q': query , 'user': user_pk},
      success: callback
    });
  }