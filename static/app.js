function Search() {
	keys = document.getElementById("search").value.split(",")
	var newkeys = [];
	keys.forEach(function(key){
		newkeys.push(encodeURIComponent(key.trim()));
	});
	window.location.assign("/posts/?tags=" + newkeys.join(","))
}

saved_tags = "";
function update_tags() {
	var http = new XMLHttpRequest();
	var url = "/tags/";

	var video_id=document.getElementsByClassName("videobox")[0].id;
	saved_tags = document.getElementById("tags").value;
	tags_changed(saved_tags);
	var keys = document.getElementById("tags").value.split(",")
	var newkeys = [];
	keys.forEach(function(key){
		newkeys.push(encodeURIComponent(key.trim()));
	});
	tags = newkeys.join(",");

	var params = "video_id=" + video_id + "&tags=" + tags;
	http.open("POST", url, true);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	http.onreadystatechange = function() {//Call a function when the state changes.
	    if(http.readyState == 4 && http.status == 200) {
			console.log(http.responseText);
	    }
	}
	http.send(params);
}

function tags_changed(new_val){
	var tag_button = document.getElementById("tag-button");
	if(new_val != saved_tags){
		if(tag_button.classList.value.indexOf("active") == -1){
			tag_button.classList.value = "tag-button active";
		}
	} else {
		if(tag_button.classList.value.indexOf("active") != 1){
			tag_button.classList.value = "tag-button";
		}
	}
} 

document.addEventListener("DOMContentLoaded", function() {
	var results = document.getElementsByClassName("search-result-img");
	
	for(i = 0; i < results.length; i++){
		e = results[i];
		var a = Math.random() * 10 - 5;
		e.style.transform = 'rotate(' + a + 'deg)';
	}

	var tag_button = document.getElementById("tag-button");
	if(tag_button != null){
		var tag_input = document.getElementById("tags");
		saved_tags = tag_input.value;
	}
});
