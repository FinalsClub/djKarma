$(document).ready(function() {
  var editing = false;
  var edit_file_element = $('#file-actions').find('.edit-file');
  // inject the note's html into the page
  // this method is used to preserve css data
  // in the source document without overriding
  // KarmaNotes's css
  var doc = $('#noteframe')[0].contentWindow.document;
  var $body = $('body',doc);
  $body.html(view_file_html);
  autoResize('noteframe');

  $('.edit-file').click(function(e){
    editing = !editing;
    if(editing === true){
      console.log('edit file. ');
      edit_file_element.html(edit_file_element.html().replace("Edit","Done"));
      $('#file-title').hide();
      $('#file-title-editable-input').val(view_file_title);
      $('#file-title-editable').show();
      $('#file-description').hide();
      $('#file-description-editable-input').val(view_file_description);
      $('#file-description-editable').show();
    }
    else{
      console.log('submit file edits');
      validateAndSubmitFileMeta();
      edit_file_element.html(edit_file_element.html().replace("Done","Edit"));
      $('#file-title').show();
      $('#file-title-editable').hide();
      $('#file-description').show();
      $('#file-description-editable').hide();
    }
  });

  
    
});

// Resize the iframe upon html injection
// Note: IE6 does not support contentWindow
// Test this case
function autoResize(id){
    var newheight;
    var newwidth;

    if(document.getElementById){
      newheight=document.getElementById(id).contentWindow.document .body.scrollHeight;
      newwidth=document.getElementById(id).contentWindow.document .body.scrollWidth;
    }

    document.getElementById(id).height = (newheight) + "px";
    //document.getElementById(id).width= (newwidth) + "px";
    //alert('height: ' + newheight);
}

// Validate file meta input fields and send request
function validateAndSubmitFileMeta(){
    do_submit = false;
    metaData = {'file_pk': view_file_pk};
    title_input = $.trim($('#file-title-editable-input').val());
    description_input = $.trim($('#file-description-editable-input').val());
    //console.log(description_input);
    //console.log(view_file_description);
    if(title_input !== "" && title_input !== view_file_title){
      metaData.title = $.trim($('#file-title-editable-input').val());
      do_submit = true;
    }
    if(description_input !== "" && description_input !== view_file_description){
      metaData.description = $.trim($('#file-description-editable-input').val());
      do_submit = true;
    }
    if(do_submit){
      console.log('/editFileMeta request');
      console.log(metaData);
      $.ajax({
        url: "/editFileMeta",
        type: 'POST',
        data: metaData,
        success: function(data) {
            if(data.status === "success"){
              console.log("successfully edited file meta");
              reflectNewFileMeta(data);
            }
        },
        dataType: "json"
      }); // end ajax
    } // end if(do_submit)
}

// Update the script and html state to reflect new file attributes
// Called from processAndSubmitFileMeta on successful POST
function reflectNewFileMeta(data){
  if('title' in data){
    view_file_title = data.title;
    $('#file-title').html(view_file_title);
  }
  if('description' in data){
    view_file_description = data.description;
    $('#file-description').html(view_file_description);
  }

}