//env_path.js

Sortable.create(ns_DEV, { 
	group: "DEV"
 });

Sortable.create(s_DEV, {
	group: "DEV"
});

Sortable.create(ns_TEST, { 
	group: "TEST"
 });

Sortable.create(s_TEST, {
	group: "TEST"
});

Sortable.create(ns_STAGING, { 
	group: "STAGING"
 });

Sortable.create(s_STAGING, {
	group: "STAGING"
});

Sortable.create(ns_LIVE, { 
	group: "LIVE"
 });

Sortable.create(s_LIVE, {
	group: "LIVE"
});

function submitPath() {

	var DEV = [];
	var devdiv = $('#s_DEV').find('.list-group-item');
	for( i = 0; i < devdiv.length; i++ ){
		DEV.push( devdiv[i].innerHTML );
	}

	var TEST = [];
	var testdiv = $('#s_TEST').find('.list-group-item');
	for( i = 0; i < testdiv.length; i++ ){
		TEST.push( testdiv[i].innerHTML );
	}

	var STAGE = [];
	var stagediv = $('#s_STAGING').find('.list-group-item');
	for( i = 0; i < stagediv.length; i++ ){
		STAGE.push( stagediv[i].innerHTML );
	}

	var LIVE = [];
	var livediv = $('#s_LIVE').find('.list-group-item');
	for( i = 0; i < livediv.length; i++ ){
		LIVE.push( livediv[i].innerHTML );
	}

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			if ( xhttp.responseText == 200 ){
				window.location.href = window.location.href
			} else {
				window.location.pathname = '/paths.html' 
			}
		}
	};
	xhttp.open("POST", "/AJAX" + window.location.pathname, true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	var msg = "dev=" + DEV;
	msg = msg + "&test=" + TEST;
	msg = msg + "&stage=" + STAGE;
	msg = msg + "&live=" + LIVE;
	xhttp.send( msg );

}