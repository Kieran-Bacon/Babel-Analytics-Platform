$(document).ready(function(){
	// In order of form list, Description is left out as it is not required.
	var formCheck = [false,false,false,false,false,true,false,false];

	$('#machine-tick').hide();
	$('#machine-cross').hide();
	$('#a-tick').hide();
	$('#a-cross').hide();
	$('#m-tick').hide();
	$('#m-cross').hide();
	$('#s-cross').hide();
	$('#name-tick').hide();
	$('#name-cross').hide();


	$('#machine-address').focusout( function() {
		var ip_pattern = /[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+/g;
		var web_pattern = /[a-zA-Z]*[.][a-zA-Z]+[.][a-zA-Z]+/g;
		
		var str = $('#machine-address').val();
		var iptest = ip_pattern.test( str );
		var webtest = web_pattern.test( str )

		if( iptest || webtest ){
			formCheck[0] = true;
			$('#machine-tick').show();
			$('#machine-cross').hide();
		} else {
			$('#machine-tick').hide();
			$('#machine-cross').show();
		}

		machineValidation();
	});
	
	$('#a-port-num').focusout( function() {
		var pattern = /^[0-9]+$/g;
		var patternTest = pattern.test( $('#a-port-num').val() );

		if( patternTest && $('#a-port-num').val() != $('#m-port-num').val() && $('#a-port-num').val() != $('#ssh-port-num').val()){
			formCheck[1] = true;
			$('#a-tick').show();
			$('#a-cross').hide();
		} else {
			$('#a-tick').hide();
			$('#a-cross').show();
		}

		machineValidation();
	});
	
	$('#m-port-num').focusout( function() {
		var pattern = /^[0-9]+$/g;
		var patternTest = pattern.test( $('#m-port-num').val() );

		if( patternTest && $('#m-port-num').val() != $('#a-port-num').val() && $('#m-port-num').val() != $('#ssh-port-num').val()){
			formCheck[2] = true;
			$('#m-tick').show();
			$('#m-cross').hide();
		} else {
			$('#m-tick').hide();
			$('#m-cross').show();
		}
		machineValidation();
	});

	$('#ssh-port-num').focusout( function() {
		var pattern = /^[0-9]+$/g;
		var patternTest = pattern.test( $('#ssh-port-num').val() );

		if( patternTest && $('#ssh-port-num').val() != $('#a-port-num').val() && $('#ssh-port-num').val() != $('#m-port-num').val()){
			formCheck[5] = true;
			$('#s-tick').show();
			$('#s-cross').hide();
		} else {
			$('#s-tick').hide();
			$('#s-cross').show();
		}
		machineValidation();
	});

	$('#machine-name').focusout( function() {
		if( ($('#machine-name').val() != "") && (($('#machine-name').val()).length < 25) )  {
			formCheck[3] = true;
			$('#name-tick').show();
			$('#name-cross').hide();
		} else {
			formCheck[3] = false;
			$('#name-tick').hide();
			$('#name-cross').show();
		}
	});


	$('#ssh-key-switch').change(function() {
    	if ($(this).is(':checked')) {
        	$('#ssh-password-group').hide();
        	$('#ssh-upload-group').show();
    	} else {
    		$('#ssh-password-group').show();
        	$('#ssh-upload-group').hide();
    	}
	});

});

function machineValidation() {
	
	if (($('#machine-address').val() != "") && (($('#a-port-num').val() != "") || ($('#m-port-num').val() != "") || ($('#ssh-port-num').val() != ""))){

		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (xhttp.readyState == 4 && xhttp.status == 200) {
				var response = JSON.parse( xhttp.responseText );
				if ($('#a-port-num').val() != ""){
					if (response.a_port == "false"){
						var alert_message = new PNotify({
							title: 'Invalid Machine and Analytics port.',
							text: 'There already exists a analytics server using the port ' + $('#a-port-num').val() +'.',
							type: 'error',
							styling: 'bootstrap3'
						});

						$('body').append(alert_message);
					}
				}

				if ($('#m-port-num').val() != ""){
					if (response.m_port == "false"){
						var alert_message = new PNotify({
							title: 'Invalid Machine and Management Port',
							text: 'There already exists a analytics server using the port ' + $('#m-port-num').val() +'.',
							type: 'error',
							styling: 'bootstrap3'
						});

						$('body').append(alert_message);
					}
				}

				if ($('#ssh-port-num').val() != ""){
					if (response.ssh_port == "false"){
						var alert_message = new PNotify({
							title: 'Invalid Machine and ssh port',
							text: 'There already exists a analytics server using the port ' + $('#ssh-port-num').val() +'.',
							type: 'error',
							styling: 'bootstrap3'
						});

						$('body').append(alert_message);
					}
				}


			}
		};
		xhttp.open("POST", "/AJAX/add_server.py", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		var msg = "machine_address=" + $('#machine-address').val();
		msg = msg + "&a_port=" + $('#a-port-num').val();
		msg = msg + "&m_port=" + $('#m-port-num').val();
		msg = msg + "&ssh_port=" + $('#ssh-port-num').val();
		xhttp.send( msg );
		
	}
}





