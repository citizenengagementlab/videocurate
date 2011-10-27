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
		
		//Control tabs in secondary content
		$("#latest").css({"left": $("#latest").width()});
		//Click handler
		$("#secondary>h3>a").click(function(e){
			e.preventDefault();
			var target = $(this).attr("href");
			$("#secondary ul").animate({"left": 0});
		});
	}
);
