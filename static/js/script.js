/* Author:
   Benjamin Wilkins
   Josh Levinger
   Citizen Engagement Laboratory
*/

DEBUG = true;

$(document).ready(
	function() {
		
		//ajax comments
		media = '/static/ajaxcomments'
    $('div#reviews form').submit(function() {
      ajaxComment({'media': media});
        return false;
    });
		
		//inline results embed
		$("ul#results a img").click(function(e) {
		  var clicked = $(this);
      inline_url = clicked.parent('a').attr('href')+"inline/";
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
  			return tags.val()? tags.val() + ", " + tag : tag;
  		});
  		return false;
  	});
  	
	  //location autocomplete
    $("#location").autocomplete("/locations/list/", { multiple: false, width:185 });
	  
	  //time display in local tz
	  $('.comment_date').each(function() {
	    var epoch = $(this).attr('title');
	    var d = new Date(epoch*1000);
	    $(this).html(d.toLocaleDateString() + " " + d.toLocaleTimeString());
	  });
	  
	  //upvoting
	  $('.upvote').click(function(e) {
	  	e.preventDefault();
  		var clicked = $(this);
	    var num_votes = $.get(this.href,{},function vote_callback(result) {
	      //var x = $.parseJSON(result);
	      var data = $.parseJSON(result);
	      //how do you get the initially selected object here?
	      clicked.html(data.num_votes + " votes");
	      clicked.css('color','green');
	    })
	    return false;
	  });
	  
	  //flagging
	  $('.flag').click(function() {
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
		$("#embed").children().attr("width", "100%")
		
		//frontpage add link
		//don't pass embed url if none entered
		$("#banner_add input[type=submit]").click(function(event) { 
		  if ($("#embed_url").val() == "") {
		    event.preventDefault();
		    window.location.assign('/add');
		    //don't use replace, that breaks the back button
		  }
		});
				
		//hide banner section on add or search pages
		if ( window.location.href.match(/\/add|search/) ) {
			$("#banner").hide();
		}
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