/* Author:
   Benjamin Wilkins
   Josh Levinger
   Citizen Engagement Laboratory
*/

DEBUG = true;

$(document).ready(
	function() {
	  //location autocomplete
    $("#location").autocomplete("/locations/list/", { multiple: false, width:185 });
	  
	  //upvoting
	  $('.upvote').click(function() {
	    num_votes = $.get(this.href,{},function vote_callback(result) {
	      if (DEBUG)console.log(result);
	      //how do you get the initially selected object here?
	      //$('.upvote').html(result.num_votes+" votes");
	      $('.upvote').css('color','green');
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
	        val = $('select.flag_type option:selected').val();
	        if (DEBUG) console.log('flag '+val);
	        url = $('.flag')[0].href;
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