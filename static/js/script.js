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
	}
);
if (true) {};