$(document).ready(function() {
	alert('Please work')

	$(".btn btn-success").click(function(){
		var value = $$('#eid_select').val()
		alert('This is an alert right' + value)

	});

	//$('#user_datatable').DataTable( {
	//	"scrollY":        "200px",
	//	"scrollCollapse": true,
	//	"paging":         false
	//} );
} )