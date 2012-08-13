function initializeBrowseView(){
$.getJSON('/browseBySchool/', function(schoolsArr) {
    $.each(schoolsArr, function(idx, school) {
      // add a schoolBtn for each school;
      $('#searchBySchool').prepend(
        $('<div/>', {class:'schoolBtn',
                     id:   school._id + "-Btn", text: school.name})

      );
      // add a coursesOfSchool div immediately following;
      $('#' + school._id + '-Btn').after(
        $('<div/>', {class:'coursesOfSchool',
                     id: slugify(school.name) + '-Courses'}) 
      );
      // school.name.replace... fixes issue with spaces in css id!
      // Can't believe I missed that :)
      // add the courses inside coursesOfSchool;
      $.each(school.courses, function(idx, course) {
        $('#' + slugify(school.name) + '-Courses').append(
          /*
          $('<div/>', {id: course._id,
                       class: 'courseBtn',
                       text: course.title})
          */

          "<div class=\"course courseBtn\" id=\""+course._id+"\">"
          +"<div class=\"folder icon\">"
            +"<img src=\"/static/img/icon-folder.png\">"
          +"</div>"
          +"<div class=\"course-title\">"
            +"<a href=\"#\">"+course.title+"</a>"
            +"<div class=\"course-info\">"
              +"<span class=\"instructor\">"+ course.instructor+"</span> <i class=\"icon-paper-clip\"></i><a href=\"#\">"+ course.num_notes +" notes</a>"
            +"</div> <!-- .course-info -->"
          +"</div> <!-- .course-title -->"
          +"<div class=\"upload\">"
            +"<a class=\"button course-upload\" school-pk=\""+ school._id+"\" school-name=\""+ school.name+"\" course-name=\""+ course.title+"\"course-pk=\""+ course._id+"\"  data-toggle=\"modal\" href=\"#upload\">Upload notes</a>"
          +"</div>"
          +"<div style=\"clear:both\"></div>"
        +"</div>" <!-- .course -->

        );
        $('#' + slugify(school.name) + '-Courses').append(
          $('<div/>', {class: 'notesOfCourse'})
        );
      });
    });
  $('.coursesOfSchool').hide();
  });

  // =========================================================================
  // toggle to browseForNotes "page" and back;
  $('#browseForNotesBtn').click(function (event) {
    // $('#drop-area').fadeToggle();
    // $('#browseForNotes').fadeToggle();
    //if ($("#searchForNotesBtn").text() == "Search") {
      $('#drop-area').hide();
      $('#browseForNotes').fadeIn(1000);
      //$("#searchForNotesBtn").text("Upload");
    //} else {
    //  $('#browseForNotes').hide();
    //  $('#drop-area').fadeIn(1000);
    //  $("#searchForNotesBtn").text("Search");
    });
  $('#uploadNotesBtn').click(function (event) {
      $('#browseForNotes').hide();
      $('#drop-area').fadeIn(1000);
  });

  // =========================================================================
  // schoolBtn click handler: 1) clicking on open school closes it; clicking on
  // closed school opens it and closes any open school; 2) retrieves notes for
  // all courses of the school;
  $('#searchBySchool').on("click", ".schoolBtn", function() {
    var clickedWasNotOpen = !$(this).hasClass('open');
    // target 'em all (tough for the CPU);
    $('.coursesOfSchool').slideUp('normal');
    // again, do 'em all!
    $('.schoolBtn').removeClass('open');
    if (clickedWasNotOpen) {
      $(this).addClass('open').next().slideDown('normal');
    }
    // fetch the notes if not already loaded;
    if (!$(this).hasClass('hasNotes')) {
      $(this).addClass('hasNotes');
      var schoolID = this.id.slice(0, -4);
      // Send user id, if logged in, to /notesOfSchool
      var reqTime = new Date().getTime();
      }
  });

  //=================================
  // courseBtn click handler: clicking on open course closes it; clicking on
  // closed course opens it and closes any open course;
  $('#searchBySchool').on("click", ".courseBtn", function() {
    // open course accordion to display notes;
    var clickedWasNotOpen = !$(this).hasClass('open');
    // get course id from courseBtn
    var courseID = this.id;
    console.log("**** 1: courseBtn click id: "+ courseID + " populated: "+$(this).next().hasClass('populated'));
    /****************** JSON notesOfCourse ************************/
    var reqTime = new Date().getTime();
    // Only perform the request if the corresponding notesOfCourse div doesn't have the 'populated' class
    if(!$(this).next().hasClass('populated')){
      $.getJSON('/browseByCourse/' + courseID, function(noteArray) {
      //console.log("/notesOfCourse/ in " + (new Date().getTime() - reqTime)/1000+"s");
      reqTime = new Date().getTime();
        // validate json
        //alert(schoolArr);
      
        // TESTING: below block verifies response JSON is valid
        //try{
        //  var theJson = $.parseJSON(schoolArr);
        //  alert('good json!');
        //}catch(err){
        //  alert('malformed json!');
        //}

        // returns a one-element array: [ {
        //   id: xxx,
        //   name: "Harvard",
        //   courses: [ {...}, {...}, {....} ]
        // } ]
        // Holds the HTML representation of all the selected course's notes
        var listItems = "";
        $.each(noteArray[0].notes, function(idx, note) {
            //console.log(note);

            // Voting widget attributes to be modified based on vote state
            // If user canvote, display voting widgets non-faded
            var vote_opacity = 1;
            var vote_up_img = "up.png";
            var vote_down_img = "down.png";
            
            // The user cannot vote, and has not voted on this note
            // Display voting widgets faded
            //console.log(parseInt(note.canvote));
            if(parseInt(note.canvote) == 0){
              vote_opacity = .3;
            }
            // If the user cannot vote, and has all ready voted, 
            // display voting arrows accordingly
            else if(parseInt(note.vote) !== 0){
              // upvote has been cast
              if(parseInt(note.vote) == 1){
                vote_up_img = "up-voted.png";
              }
              else if(parseInt(note.vote) == -1){
                vote_down_img = "down-voted.png";
              }
            }
            // Inject note data div
            listItems += "<div class=\"file row-fluid\">"
          +"<div class=\"file icon\"></div>"
          +"<div class=\"file-title\">"
            +"<a href=\"#\">"+note.notedesc+"</a>"
          +"</div>";


            listItems += "<div class=\"note\">"
              +"<div class=\"file-info-action hide row\">"
              +"<div class=\"file-info\"> "
              +"<span class=\"user\">Uploaded by <a href=\"#\"><i class=\"icon-user\"></i>"+note.user+"</a></span>"
              +"<span class=\"download\"><a class=\"view-file\" id=\""+note._id+"\" href=\"#\"><i class=\"icon-paper-clip\"></i>View file</a></span>";

            if (parseInt(note.canvote) === 1){
              listItems += "<span class=\"karma-points\">OWNED</span>";
            }
            else{
              listItems += "<span class=\"karma-points\">-10 points</span>";
            }
            listItems += "<span class=\"views\">"+note.views+" Views </span>"
              +"</div>";

            listItems += "<div class=\"file-actions\" id=\"file-"+note._id+"\">"
                +"<a href=\"#\" class=\"vote upvote\"><i class=\"icon-heart\"></i>Like ("+note.upvotes+")</a>"
                +"<a href=\"#\" class=\"vote downvote\"><i class=\"icon-flag\"></i>Flag</a>"
                +"<a href=\"#\"><i class=\"icon-pencil\"></i>Edit</a>"
                +"<a href=\"#\"><i class=\"icon-remove-circle\"></i>Delete</a>"
              +"</div></div></div></div>";
            /*
            listItems += "<div class=\"note\">"
                          +"<div style=\"display:inline-block;text-align:center\">"
                            +"<img style=\"opacity:"+vote_opacity+"\" class=\"vote upvote "+note.canvote+"\" id=\""+note._id+"-upvote\" src=\"{{STATIC_URL}}img/"+vote_up_img+"\"/>"
                            +"<div id=\""+note._id+"-pts\">"+note.pts+"</div>"
                            +"<img style=\"opacity:"+vote_opacity+"\" class=\"vote downvote "+note.canvote+"\" id=\""+note._id+"-downvote\" src=\"{{STATIC_URL}}img/"+vote_down_img+"\"/>"
                          +"</div>"
                          +"<div style=\"display:inline-block;margin-left:5px\">"
                            +"<div><a href=\"/file/"+note._id+"\">" + note.notedesc + "</a></div>"
                            +"<div>"+ note.views+" views </div>"
                            +"<div>Uploaded by " + note.user + "</div>"
                          +"</div>"
                          +"</div>";
                                    //alert(course._id);
                                    */
          
        });
        /* Instead of creating notesOfCourse, fill it
        $('#' + courseID).after(
              $('<div class="notesOfCourse" style="display: none;">' +
                listItems + '</div>')
          );
        */
        $('#' + courseID).next().append(listItems);
      //console.log("/notesOfCourse/ html injection " + (new Date().getTime() - reqTime)/1000+"s");
        $('#' + courseID).next().addClass('populated');

        
      }); // end getJson
    } // end if notesOfCourse loaded check
    
      // target 'em all (tough for the CPU);
      console.log("2: Slide up all notesOfCourse");
      $('.notesOfCourse').slideUp('normal');
      // again, do 'em all!
      $('.courseBtn').removeClass('open');
      if (clickedWasNotOpen) {
        console.log("3: Slide down this notesOfCourse: "+$(this).next());
        $(this).addClass('open').next().slideDown('normal');
        //console.log("slide down notesOfCourse w id: "+ $(this).next().attr("id"));
      
    }
    /****************** END JSON notesOfCourse ********************/
  });

  // Vote click-listener
  $('#searchBySchool').on("click", ".vote", function() {
    // check if user canvote on this note
    //if($(this).hasClass('true')){
      // note_id = [note_pk]-[upvote/downvote]
      var note_id = $(this).attr('id');
      var vote = 0;
      if(note_id.split("-")[1] === "downvote"){
        vote = -1;
      }
      else if(note_id.split("-")[1] === "upvote"){
        vote = 1;
      }
      //alert('vote: ' + note_id.split("-")[1] + " : "+ vote);
      if(vote === 0)
        return;
      
      $.ajax({
                // /vote/note_pk?v=vote_value
                url: "/vote/"+note_id.split("-")[0],
                data: {'vote': vote},
                success: function(data) {
                  //alert(data);
                    if (data === "success"){
                      // Increment/Decrement pt count on page
                      // Display voted arrow img
                      // Set vote widget opacities to 1
                      var curPts = $('#'+note_id+"-pts").text();
                      if(vote === 1){
                        $('#'+note_id).attr('src','{{STATIC_URL}}img/up-voted.png');
                        var curPts = $('#'+note_id.split("-")[0]+"-pts").text();
                        console.log(curPts);
                        $('#'+note_id.split("-")[0]+"-pts").text(parseInt(curPts)+1);
                      }
                      else if(vote === -1){
                        $('#'+note_id).attr('src','{{STATIC_URL}}img/down-voted.png');
                        var curPts = $('#'+note_id.split("-")[0]+"-pts").text();
                        console.log(curPts);
                        $('#'+note_id.split("-")[0]+"-pts").text(parseInt(curPts)-1);
                      }
                      // set vote widget opacities to 1
                      $('#'+note_id.split("-")[0]+"-upvote").attr('style','opacity:1');
                      $('#'+note_id.split("-")[0]+"-downvote").attr('style','opacity:1');
                    }
                    else{
                      alert(data);
                    }
                },
                dataType: "text"
            });
  });

}// end initializeBrowseView()

  var fileListHeaderDrawn = false;
  function nodeToString ( node ) {
    var tmpNode = document.createElement( "div" );
    tmpNode.appendChild( node.cloneNode( true ) );
    var str = tmpNode.innerHTML;
    tmpNode = node = null; // prevent memory leaks in IE
    return str;
  }

  function slugify(Text)
  {
      return Text
          .toLowerCase()
          .replace(/[^\w ]+/g,'')
          .replace(/ +/g,'-')
          ;
  }