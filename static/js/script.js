/* Author:
   Benjamin Wilkins
   Josh Levinger
   Citizen Engagement Laboratory
*/

DEBUG = true;

$(document).ready(
	function() {
		
		//add tags
		$('a#show_add_tags').click(function(e) {
		  e.preventDefault();
		  $('form#add_tags').show();
		  $('a#show_add_tags').hide();
		});
		$('form#add_tags').submit(function(e) {
		  e.preventDefault();
		  $.post($(this).attr('action'),
		      {'tags':$('form#add_tags input#id_tags').val()},
		      function(response){
		        if(DEBUG) console.log(response.success);
		        for (t_id in response.success) {
		          t = response.success[t_id];
		          $("ul.tags").append("<li class='tag'><a href='/search?tag="+t+"'>"+t+"</a></li>");
		        }
		      },'json');
		  $('form#add_tags input#id_tags').val("");
		  $('form#add_tags').hide();
		  $('a#show_add_tags').show();
		  return false;
		});
		
		//ajax comments
		media = '/static/ajaxcomments'
    $('div#reviews form').submit(function(e) {
      e.preventDefault();
      ajaxComment({'media': media});
        return false;
    });
		
		//inline results embed
		$("ul#results a.thumb").click(function(e) {
		  e.preventDefault();
		  var clicked = $(this);
      inline_url = clicked.attr('href')+"inline/";
		  var num_votes = $.get(inline_url,{},function view_inline_callback(result) {
	      if(DEBUG) console.log('view_inline_callback');
	      inline_html = $(result);
	      if(DEBUG) console.log(result);
	      var parent = clicked.parents('li');
	      if(DEBUG) console.log(parent);
	      parent.after(inline_html);
	      parent.hide();
	      
	      $('a.hide_inline').click(function() {
	        $(this).parents('.inline_view').hide();
	        $(this).parents('li').prev().show();
	      })
	    })
		  
		  return false;
		});
		
  	//Tag Cloud Simple Tagging
  	$("form #tag_cloud ul>li>a").click(function(e){
  		e.preventDefault();
  		var tag = $(this).html();
  		var tags = $("#id_tags");
  		if(DEBUG) console.log(tag);
  		if(DEBUG) console.log(tags);
  		tags.val(function(){
  			//ternerary operator checking if we should prepend ", "
  			return tags.val()? tags.val() + ", " + tag : tag;
  		});
  		return false;
  	});
  	
	  //location autocomplete
    $("#location").autocomplete("/locations/list/", { multiple: false, width:185 });
    
    //add tag autocomplete
    $("form#add_tags #id_tags").autocomplete("/tags/json", { multiple: true });
	  
	  //time display in local tz
	  $('.comment_date').each(function() {
	    var epoch = $(this).attr('title');
	    var d = new Date(epoch*1000);
	    $(this).html(d.toString('M/d/yyyy h:mm tt'));
	    //$(this).html(d.toLocaleDateString() + " " + d.toLocaleTimeString());
	  });
	  
	  //upvoting
	  $('.upvote').click(function(e) {
	  	e.preventDefault();
  		var clicked = $(this);
  		clicked.css("background-image", "url(/static/images/spinner.gif)");
	    var num_votes = $.ajax({
	      url:this.href,
	      cache: false,
	      dataType: "json",
	      data:{},
	      success: function vote_callback(result) {
	        if (DEBUG) console.log(result);
        	$(".votes").html(result.num_votes);
      		clicked.css("background-image", "url(/static/images/check.png)");
	      }
	    })
	    return false;
	  });
	  
	  //flagging
	  $('.flag').click(function(e) {
	    e.preventDefault();
	    if ($(this).next('.flag_type').length) { return false; }
	    $("<select class='flag_type'><option value='NONE'>Why?</option>"
	      + "<option value='INAPP'>Inappropriate</option>" 
	      + "<option value='OFFNS'>Offensive</option>" 
	      + "<option value='SPAM'>Spam</option></select>").insertAfter(this);
	      $('select.flag_type').change(function() {
	        var val = $('select.flag_type option:selected').val();
	        if (DEBUG) console.log('flag '+val);
	        var url = $('.flag')[0].href;
	        if (DEBUG) console.log(url);
	        $.get(url,{reason:val},function flag_callback(result) {
	          if (DEBUG) console.log('flag_callback');
	          if (DEBUG) console.log(result);
	          $('select.flag_type').hide();
      	    $('.flag').html('Flagged').css('color','green');
	        });
    	  });
    return false;
	  });
	  
		//set embed width to 100%
		$("#embed").children()
			.attr("width", "100%")
			.children()
			.filter("embed")
			.attr("width", "100%");
		
		//frontpage add link
		//don't pass embed url if none entered
		$("form#add_form input[type=submit]").click(function(e) {
	    e.preventDefault();
		  if ($("#embed_url").val() == "") {
		    window.location.assign('/add');
		    //don't use replace, that breaks the back button
		  } else {
		    $("form#add_form").submit();
		  }
		$(this).parent().submit();
		});
				
		//Copy GET Request URL to proper field on add page.		
		function getEmbedUrl(){
			var urlExplode = window.location.href.split("?");
			var getMap;
			if (getMap = urlExplode[1]) {
				var keyVals = getMap.split("&");
				var getVariables;
				for (var i = 0; i < keyVals.length; i++) {
					getVariable = keyVals[i].split("=");
					if (getVariable[0]==="embed_url"){
						return unescape(getVariable[1]);
					}
				}	
			}
		}
		if ( window.location.href.match(/\/add/) ) {
			var embed_url = getEmbedUrl();
			if (embed_url) {
				$("#id_url").val(embed_url);
				$("#id_preview_button").click()
					.hide();
			}
		}
		
		//setup slider
		var slider = $("#secondary .slide");
		var groups = slider.children("ul");
		slider
			.css({"width": (groups.length * 100).toString() + "%", "position": "relative"})
			.children("ul")
				.css({"width": slider.parent().width(), "float": "left"})
				.parents("#secondary")
				.children(".tabs")
				.children(".tab:first-child")
				.children("h3")
				.children("a")
				.addClass("active");

		//Click handler
		$("#secondary .tabs h3>a").click(function(e){
			e.preventDefault();
			if ($(this).hasClass("active")) {
				return false;
			} else {
				$("#secondary .tabs a.active").removeClass("active");
				var target = $(this);
				target.addClass("active");
				var position = $(target.attr("href")).position();
				slider.animate({ "left": 0 - position.left });
			}
		});
	}
);