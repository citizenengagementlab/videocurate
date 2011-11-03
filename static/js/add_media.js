DEBUG = true;

var url = new RegExp(/^(http[s]?:\/\/){0,1}(www\.){0,1}[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,5}[\.]{0,1}/);

$(document).ready(function onload(){
  //enable the preview button
  $("input#id_url").keypress(function(e){
    //if the user hits return, process the preview button, not the form submit
    if(e.which == 13) {
      $("input#id_preview_button").click();
    }
  });
  $('input#id_url').blur(function(e) {
    //check to see if it's a url first
    if (url.test($("input#id_url").val())) { 
      $("input#id_preview_button").click();
    }
  });
  $("input#id_url").bind('paste', function(e) {
    //check to see if it's a url first
    if (url.test($("input#id_url").val())) { 
      setTimeout(function() {
        $("input#id_preview_button").click();
      }, 100);
    }
  });
  
  $("input#id_preview_button").click(function(e) {
    e.preventDefault();
    theURL=$("#id_url").val();
    if (theURL == "") { $("label[for=id_url]").addClass("error"); return false; }
    else { $("label[for=id_url]").removeClass("error"); }
    $("#preview").show();
    $.ajax({
      type:'POST',
      url:"/embed/cache/",
      data:{url:theURL,maxwidth:"620"},
      dataType:'json',
      success: function embedly_callback(data) {
        $('ul.messages').hide();

        if (DEBUG) console.log('embedly callback');
        if (DEBUG) console.log(data);        
        if(data.exists) {
          if (DEBUG) console.log('already have the video');
          showMessage("Sweet video; it's so good, we already have a copy. Want to add your review and tags "
           + "<a href='/search?url="+escape(data.original_url)+"'>here</a>?","info");
        } else {
          if (data.html == "") {
            showMessage("Sorry, we can't get an embed for that url.<br>Check to see if the url is complete, or has a typo. The owner may also have disabled embedding on the hosting platform.","info");
          } else {
            //we're good to go
            $('#preview #preview_html').html(data.html);
            if(data.url) { $('#addform #id_url').val(data.url); }
            $('#addform #id_title').val(data.title);
            $('#addform #id_author_name').val(data.author_name);
            $('#addform #id_author_url').val(data.author_url);
            $('#addform #id_resolution').val(data.width+'x'+data.height);
            $('#preview #preview_description').html("<b>Original Description:</b> "+data.description);
            thirdparty_extras(data);
          }
        }
        $("#preview .spinner").hide();
      },
      error: function embedly_error(data) {
        showMessage("Sorry, we weren't able to embed that url. Check to see if the url is complete, or has a typo.","error");
      }
    });
    return false;
  });
  
  //hide metadata by default
  $('<a href="#" class="show_hidden">Show Metadata</a>').insertBefore('fieldset.hidden');
  $('.show_hidden').toggle(function() {
      $(this).next('.hidden').show();
      $(this).html('Hide Metadata');
      return false;
    },function() {
      $(this).next('.hidden').hide();
      $(this).html('Show Metadata');
      return false;
    });
  $('fieldset.hidden').hide();
  
  //no location specific button
  $('#no_location').click(function(e) {
    e.preventDefault();
    $('#id_location').val('No Location');
    return false;
  });
  
  
  $("input#addform_submit").click(function(e) {
    e.preventDefault();
    //do some validation client side, so we don't have to reload the page for missing fields
    required_fields = ["url","title","location","tags"]
    has_error = false;
    for (i in required_fields) {
      selector = "id_"+required_fields[i];
      if($('#addform #'+selector).val() == "") {
        has_error = true;
        $("label[for="+selector+"]").addClass("error");
      }
    }
    if (!has_error) {
      $("form#addform").submit();
    }
  });
  
});

function showMessage(message,message_class) {
  clear_text = "<br>Want to <a href='#' class='clear'>clear the fields</a> and start again?";
  msg_html = "<li class='"+message_class+"'>"+message+clear_text+"</li>";
  $('ul.messages').append(msg_html);
  $('ul.messages').show();
  setClear();
}
function setClear() {
  $('a.clear').click(function(e) {
    e.preventDefault();
    clearForm();
    return false;
  });
}
function clearForm() {
  $('form#addform')[0].reset();
}

/* functionality to get info that embedly doesn't return*/
function thirdparty_extras(data) {
  switch (data.provider_name) {
    case 'YouTube':
      return youtube_extras(data);
    case 'Vimeo':
      return vimeo_extras(data);
    case 'Flickr':
      return flickr_extras(data);
    default:
      return false;
  }
}
function youtube_extras(data) {
  youtube_query = data.url.split('=')[1] //probably good enough, gets the whole query string
  youtube_extra = $.get("https://gdata.youtube.com/feeds/api/videos?",
    {q:youtube_query,max_results:1,v:2,alt:'json'},
    function youtube_callback(response) {
      if (DEBUG) console.log('youtube callback');
      if (DEBUG) console.log(response);
      extra = {}
      entry = response.feed.entry[0];
      extra.views = entry.yt$statistics.viewCount;
      extra.license = entry.media$group.media$license.$t;
      extra.date_uploaded = entry.published.$t;
      //need to find max width/height
      append_extras(extra);
      return extra;
    });
}
function vimeo_extras(data) {
  //check for trailing slash
  last_char = data.original_url.slice(data.original_url.length-1);
  if (last_char == "/") {
    split_list = data.original_url.split('/');
    vimeo_id = split_list[split_list.length-2];
  } else {
    vimeo_id = data.original_url.split('/').pop();
  }
  vimeo_url = "http://vimeo.com/api/v2/video/" + vimeo_id + ".json";
  vimeo_extra = $.ajax({url:vimeo_url,
                      dataType:'jsonp',
                      success: function vimeo_callback(response,status,jqXHR) {
                        if (DEBUG) console.log('vimeo callback');
                        if (DEBUG) console.log(response);
                        item = response[0];
                        append_extras({
                          views:item.stats_number_of_plays,
                          date_uploaded:item.upload_date,
                          //api doesn't return license or max_res
                        })
                      }
                  });
}
function flickr_extras(data) {
  //use regex to determine photo_id
  flickr_regex = RegExp('photos/[^/]+/([0-9]+)')
  photo_id = flickr_regex.exec(data.original_url)[1]
  api_key = 'fd34c2ff0085800fd5c78c24c2b26f66'
  flickr_url = "http://www.flickr.com/services/rest/?method=flickr.photos.getInfo&format=json" +
              "&photo_id=" + photo_id +
              "&api_key=" + api_key;
  flickr_extra = $.ajax({url:flickr_url,
                    dataType:'jsonp',
                    jsonp:'jsoncallback',
                    success: function flickr_callback(response,status,jqXHR) {
                      if (DEBUG) console.log('flickr callback');
                      if (DEBUG) console.log(response);
                      flickr_license = response.photo.license;
                      //see http://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
                      switch(flickr_license) {
                        case 0: license = "unk";
                        case 1: license = "cc-by-nc-sa";
                        case 2: license = "cc-by-nc";
                        case 3: license = "cc-by-nc-nd";
                        case 4: license = "cc-by";
                        case 5: license = "cc-by-sa";
                        case 6: license = "cc-by-nd";
                        case 7: license = "none";
                        default: license = "unk";
                      }
                      append_extras({
                        views:response.photo.views,
                        license:license,
                        date_uploaded:response.photo.dates.taken //uses exif data, parse in python
                      })
                    }
                  });
}
function append_extras(extra) {
  // save the extra data to the input fields
  if (extra.max_width && extra.max_height){
    $('#addform #id_resolution').val(extra.max_width+'x'+extra.max_height); 
  };
  if (extra.views) { $('#addform #id_views').val(extra.views); }
  if (extra.license) { $('#addform #id_license').val(extra.license); }
  if (extra.date_uploaded) { $('#addform #id_date_uploaded').val(extra.date_uploaded); }
}