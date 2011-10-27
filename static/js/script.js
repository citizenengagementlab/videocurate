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
				.css({"width": "50%", "float": "left"});

		//Click handler
		$("#secondary>h3>a").click(function(e){
			e.preventDefault();
			var target = $(this).attr("href");
			switch (target) {
				case "#popular":
					slider.animate({ "left": 0 });
					break;
				case "#latest":
					slider.animate({ "left": 0-(slider.width()/2) });
					break;
				default:
					return false;
			}
		});
	}
);