function checkStatus( srv_id ){
	$.ajax({
		type:"GET",
		url: "AJAX_manage_servers_" + srv_id,
		success: function( resp ){
			var unpacked = JSON.parse( resp );
			var aTag = '<i class="green" style="font-weight: bold;">';
			var rTag = '<i class="red" style="font-weight: bold;">';

			if( unpacked.Management == "ACCEPTING" ){
				$('#mStat_'+srv_id).html(aTag + "ACCEPTING</i>");
			} else {
				$('#mStat_'+srv_id).html(rTag + "REJECTING</i>");
			}

			if( unpacked.Analytic == "ACCEPTING" ){
				$('#aStat_'+srv_id).html(aTag + "ACCEPTING</i>");
			} else {
				$('#aStat_'+srv_id).html(rTag + "REJECTING</i>");
			}
		},
		failure: function( resp ){
			alert( resp );
		}
	})
}