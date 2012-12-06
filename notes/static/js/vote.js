  // Vote click-listener
  $('.voter').on("click", ".vote", function() {
    // check if user canvote on this note
    //if($(this).hasClass('true')){
      // note_id = [note_pk]-[upvote/downvote]
      var note_id = $(this).attr('id');
      var type    = $(this).attr('type');
      var vote = 0;
      if(type === "flag"){
        vote = -1;
      }
      else if(type === "thank"){
        vote = 1;
      }
      //alert('vote: ' + note_id.split("-")[1] + " : "+ vote);
      if(vote === 0)
        return;

      $.ajax({
                // /vote/note_pk?v=vote_value
                url: "/vote/"+note_id,
                data: {'vote': vote},
                success: function(data) {
                  //alert(data);
                    if (data === "success"){
                      // Increment/Decrement pt count on page
                      // Display voted arrow img
                      // Set vote widget opacities to 1
                      var curPts = $('#'+note_id+"-pts").text();
                      if(vote === 1){
                        //$('#'+note_id).attr('src','{{STATIC_URL}}img/up-voted.png');
                        //var curPts = $('#'+note_id.split("-")[0]+"-pts").text();
                        console.log(curPts);
                        //$('#'+note_id.split("-")[0]+"-pts").text(parseInt(curPts)+1);
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
