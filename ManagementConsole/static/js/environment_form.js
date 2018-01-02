$(document).ready(function() {
	$(".select2_single").select2({
		placeholder: "Select a Environment Type"
	});

	$(".select2_multiple").select2({
          placeholder: "Select Multiple Servers",
          allowClear: true
    });
});