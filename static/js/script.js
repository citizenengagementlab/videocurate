/* Author:
   Benjamin Wilkins
   Josh Levinger
   Citizen Engagement Laboratory
*/


$(document).ready(
	function() {
		//set embed width to 100%
		$("#embed").children().attr("width", "100%")
		//hide banner section on add page
		if ( window.location.href.match(/\/add/) ) {
			$("#banner").hide();
		}
		
		//setup slider
		var slider = $("#secondary .slide");
		slider
			.css({"width": "200%", "position": "relative"})
			.children("ul")
				.css({"width": "50%", "float": "left"})
				.parents("#secondary")
				.children("h3:first-child")
				.children("a")
				.addClass("active");

		//Click handler
		$("#secondary>h3>a").click(function(e){
			e.preventDefault();
			if ($(this).hasClass("active")) {
				return false;
			} else {
				$("#secondary>h3>a.active").removeClass("active");
				var target = $(this);
				target.addClass("active");
				var link = target.attr("href");
				switch (link) {
					case "#popular":
						slider.animate({ "left": 0 });
						break;
					case "#latest":
						slider.animate({ "left": 0-(slider.width()/2) });
						break;
					default:
						return false;
				}
			}
		});
	}
);