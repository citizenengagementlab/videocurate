/* Author:
 Benjamin Wilkins
 Josh Levinger
 Citizen Engagement Laboratory
 */

var DEBUG = true;

$(document).ready(function() {
	//social media sharing tools
	$('.sharebutton').click(function(e){
	  e.preventDefault();
	  var url = $(this).attr('href');
	  var id = $(this).attr('id');
	  if (DEBUG) console.log(id+" "+url);
	  switch(id) {
	    case 'twitter_share':
	      var share_url = 'http://twitter.com/intent/tweet?via=99percentmedia&url=' + encodeURIComponent(url);
	      break;
	    case 'facebook_share':
	      var share_url = "http://facebook.com/sharer/sharer.php?"
                    + "&u=" + encodeURIComponent(url);
        break;
	  }
	  window.open(share_url,'Share','height=400,width=500');
	})
	
	//show search fields on click
	$('#show_search').click(function show(e) {
	  e.preventDefault();
	  $('#inline_search_form').toggle();
	});
	
	//Provide focus to comment for when use clicks "add your own review"
	$('a[href="#comment_form"]').click(function(e){
		e.preventDefault();
		$("html,body").animate({scrollTop: $(".comment-form").offset().top}, "normal");
		$("#id_name").focus();
	});

	//add tags
	$('a#show_add_tags').click(function(e) {
		e.preventDefault();
		$('form#add_tags').show().children().filter("#id_tags").focus();
		$('a#show_add_tags').hide();
	});
	$('form#add_tags').submit(function(e) {
		e.preventDefault();
		$.post($(this).attr('action'), {
			'tags' : $('form#add_tags input#id_tags').val()
		}, function(response) {
			if(DEBUG)
				console.log(response.success);
			for(var t_id in response.success) {
				var t = response.success[t_id];
				$("ul.tags").append("<li class='tag'><a href='/search?tag=" + t + "'>" + t + "</a></li>");
			}
		}, 'json');
		$('form#add_tags input#id_tags').val("");
		$('form#add_tags').hide();
		$('a#show_add_tags').show();
		return false;
	});
	
	//ajax comments
	var media = '/static/ajaxcomments';
	$('div#reviews form').submit(function(e) {
		e.preventDefault();
		ajaxComment({
			'media' : media
		});
		return false;
	});
	
	//inline results embed
	$("ul#results a.thumb").click(function(e) {
		e.preventDefault();
		var clicked = $(this);
		var inline_url = clicked.attr('href') + "inline/";
		var num_votes = $.get(inline_url, {}, function view_inline_callback(result) {
			if(DEBUG)
				console.log('view_inline_callback');
			var inline_html = $(result);
			if(DEBUG)
				console.log(result);
			var parent = clicked.parents('li');
			if(DEBUG)
				console.log(parent);
			parent.after(inline_html);
			parent.hide();

			$('a.hide_inline').click(function() {
				$(this).parents('.inline_view').hide();
				$(this).parents('li').prev().show();
			});
		});
		return false;
	});
	
	//Tag Cloud Simple Tagging
	$("form #tag_cloud ul>li>a").click(function(e) {
		e.preventDefault();
		var tag = $(this).html();
		var tags = $("#id_tags");
		if(DEBUG)
			console.log(tag);
		if(DEBUG)
			console.log(tags);
		tags.val(function() {
			//ternerary operator checking if we should prepend ", "
			return tags.val() ? tags.val() + ", " + tag : tag;
		});
		return false;
	});
	
	//location autocomplete
	$("#location").autocomplete("/locations/list/", {
		multiple : false,
		width : 150
	});

	//add tag autocomplete
	$("form#add_tags #id_tags").autocomplete("/tags/json", {
		multiple : true
	});

	//time display in local tz
	$('.comment_date').each(function() {
		var epoch = $(this).attr('title');
		var d = new Date(epoch * 1000);
		$(this).html(d.toString('M/d/yyyy h:mm tt'));
		//$(this).html(d.toLocaleDateString() + " " + d.toLocaleTimeString());
	});
	
	//upvoting
	$('.upvote').click(function(e) {
		e.preventDefault();
		var clicked = $(this);
		clicked.css("background-image", "url(/static/images/spinner.gif)");
		var num_votes = $.ajax({
			url : this.href,
			cache : false,
			dataType : "json",
			data : {},
			success : function vote_callback(result) {
				if(DEBUG)
					console.log(result);
				$(".votes").html(result.num_votes);
				clicked.css("background-image", "url(/static/images/check.png)");
			}
		});
		return false;
	});
	
	//flagging
	$('.flag').click(function(e) {
		e.preventDefault();
		if($(this).next('.flag_type').length) {
			return false;
		}
		$("<select class='flag_type'><option value='NONE'>Why?</option>" + "<option value='INAPP'>Inappropriate</option>" + "<option value='OFFNS'>Offensive</option>" + "<option value='SPAM'>Spam</option></select>").insertAfter(this);
		$('select.flag_type').change(function() {
			var val = $('select.flag_type option:selected').val();
			if(DEBUG)
				console.log('flag ' + val);
			var url = $('.flag')[0].href;
			if(DEBUG)
				console.log(url);
			$.get(url, {
				reason : val
			}, function flag_callback(result) {
				if(DEBUG)
					console.log('flag_callback');
				if(DEBUG)
					console.log(result);
				$('select.flag_type').hide();
				$('.flag').html('Flagged').css('color', 'green');
			});
		});
		return false;
	});
	
	//set embed width to 100%
	$("#embed").children().attr("width", "100%").children().filter("embed").attr("width", "100%");
	//remove height on images, use in browser resizing
	$("#embed").children('img').attr("height", "");

	//frontpage add link
	//don't pass embed url if none entered
	$("form#add_form input[type=submit]").click(function(e) {
		e.preventDefault();
		if($("#embed_url").val() === "") {
			window.location.assign('/add');
			//don't use replace, that breaks the back button
		} else {
			$("form#add_form").submit();
		}
		$(this).parent().submit();
	});

	//setup slider
	var slider = $("#secondary .slide");
	var groups = slider.children("ul");
	slider.css({
		"width" : (groups.length * 100).toString() + "%",
		"position" : "relative"
	}).children("ul").css({
		"width" : slider.parent().width(),
		"float" : "left"
	}).parents("#secondary").children(".tabs").children(".tab:first-child").children("h3").children("a").addClass("active");

	//Click handler for slide events
	$("#secondary .tabs h3>a").click(function(e) {
		e.preventDefault();
		if($(this).hasClass("active")) {
			return false;
		} else {
			$("#secondary .tabs a.active").removeClass("active");
			var target = $(this);
			target.addClass("active");
			var position = $(target.attr("href")).position();
			slider.animate({
				"left" : 0 - position.left
			});
		}
	});
});
