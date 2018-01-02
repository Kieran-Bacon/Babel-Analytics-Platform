$(document).ready(function() {

	wizardSetUp();
	pageSetUp();
	
	$('#http-redirect-switch').change(function() {
    	if ($(this).is(':checked')) {
        	$('#httpget-page-selector').hide();
        	$('#redirect-URL-input').show();
    	} else {
    		$('#httpget-page-selector').show();
        	$('#redirect-URL-input').hide();
    	}
	});
});

function pageSetUp(){

	var values = $('#edit').val();
	if (values != "New"){
		var inputs = values.split("-")
		$("#Poolsize").ionRangeSlider({
          from: inputs[1]
        });

	} else {
		$("#Poolsize").ionRangeSlider({
          from: 1
        });
	}
}


function wizardSetUp() {
	//Selecting and starting the Wizard
	$('#wizard').smartWizard({
        onLeaveStep:leaveAStepCallback,
        onFinish:onFinishCallback
    });

	$('#wizard_verticle').smartWizard({
		transitionEffect: 'slide'
	});

	//Create button links and disable finish
	//(as it will be used later)

	$('.buttonNext').addClass('btn btn-success');
	$('.buttonPrevious').addClass('btn btn-primary');
	$('.buttonFinish').addClass('btn btn-default');
	$('.buttonFinish').prop("disabled",true)

    function leaveAStepCallback(obj, context){

		if (context.fromStep < context.toStep){

			if(context.fromStep == 1){
				return validateStepOneForm()
			}
			else {
				return validateStepTwoForm()
			}
		} 
		else {
			if (context.fromStep == 3){
				$("#main_script_select").empty();
				$("#get_page_select").empty();				
			}
			return true;
		} 



        alert("Leaving step " + context.fromStep + " to go to step " + context.toStep);
        return validateSteps(context.fromStep); // return false to stay on step and true to continue navigation 
    }

    function onFinishCallback(objs, context){

    	var values = $('#edit').val();
    	if (values == "New"){
    		var destination = "add_service.html"
    	} else {
    		var section = values.split('-');
    		if( section[0] == 0 ){
    			var destination  = "add_version_" + section[1];
    		} else {
    			var destination = "edit_version_" + section[1];
    		}
    	}

        $.ajax({
   			type:'POST',
   			url: destination,
   			data: $('form').serialize(),
   			cache: false,
   			success: function(responseHTML){
   				window.location.pathname = responseHTML
   			}
 		});
    }
};

function validateStepOneForm(){

	range = ($("#Poolsize").val()).split(";");

	if ( !$("input[name=language]:checked").val() || !$('#srv-name-input').val() || !$('#res-name-input').val() || range[1] == "0" ){
		var alert_message = new PNotify({
			title: 'Invalid Form Entry',
			text: 'Please ensure that all required fields are entered, and that the pool size is not 0.',
			type: 'error',
			styling: 'bootstrap3'
		});

		$('body').append(alert_message);
		return false
	}

	return true;
};

function validateStepTwoForm(){

	var drpZone = $("#service-docs-upload").get(0).dropzone;
	var lang = $("input[name=language]:checked").val();
	var fileList = "";

	step_valid = false;

	//loop over uploaded files
	for (i = 0; i < drpZone.files.length; i++) { 

		var fname = drpZone.files[i].name;	//name of file
		var f_ext = fname.substr(fname.indexOf(".")).toLowerCase()	//file extension

		if (f_ext == lang){
			var opt = document.createElement('option');
			opt.innerHTML = fname;
			opt.value = fname;
			$("#main_script_select").append(opt);
			step_valid = true	
		}

		if (f_ext == ".htm" || f_ext == ".html" ){
			var opt = document.createElement('option');
			opt.innerHTML = fname;
			opt.value = fname;
			$("#get_page_select").append(opt);
		}

		fileList = fileList + fname + ","; 

	}



	$('#uploaded-files').val( fileList.slice(0,-1) )

	if( !step_valid ){
		
		var alert_message = new PNotify({
			title: 'No script files detected',
			text: "Please upload a service definition script file. The uploaded file should have a \'" + lang +  "\' file extension",
			type: 'info',
			styling: 'bootstrap3',
			addclass: 'dark'
		});

		$('body').append(alert_message);
	}


	return step_valid;
};

