$(document).ready(function(){
  getDashData( "pie" );
  getDashData( "line" );
});

function getDashData( resource ){
  var datastr = "resource=" + resource

  $.ajax({
    type:"POST",
    url:"/AJAX/dashboard.py",
    data: datastr,
    contentType: "application/x-www-form-urlencoded",
    success: function( resp ){
    	if( resp == "None" ){
    		console.log("No Environments or Services");
    	}
    	else if( resource == "pie" ){
    		pieChart( resp );
    	} else {
    		lineGraph( resp );
    	}
    },
    failure: function( resp ){
      alert( resp );
    }
  })
}

function pieChart( json ){
	var theme = getTheme();
	var pieInfo = JSON.parse( json );

	var pieData = []
	for (var i = 0; i < pieInfo.legend.length; i++ ){
		var data_point = { value: pieInfo.data[i], name: pieInfo.legend[i] };
		pieData.push( data_point );
	}

	var echartPieCollapse = echarts.init(document.getElementById('servicePie'), theme);
	echartPieCollapse.setOption({
		tooltip: {
			trigger: 'item',
			formatter: "{a} <br/>{b} : {c} ({d}%)"
		},
		legend: {
			x: 'center',
			y: 'top',
			data: pieInfo.legend
		},
		calculable: true,
		series: [{
			name: 'Service Requests',
			type: 'pie',
			radius: [25, 120],
			center: ['50%', 170],
			roseType: 'area',
			x: '50%',
			max: 40,
			sort: 'ascending',
			data : pieData
		}]
	});
}

function lineGraph( json ){
	var theme = getTheme();
	var lineInfo = JSON.parse( json );

	for( i = 0 ; i < lineInfo.environments.length; i++){

		var env = lineInfo.environments[i];
		var graphID = "env_graph_" + env.eid;

		var lineData = []
		for ( j = 0; j < env.servicesReqt.length; j++){

			var data_point = {
				name: env.servicesNames[j],
				type: 'line',
				smooth: true,
				itemStyle: {
					normal: {
						areaStyle: {
							type: 'default'
						}
					}
				},
				data: env.servicesReqt[j]
			};
			lineData.push( data_point );
		}

		var echartLine = echarts.init(document.getElementById(graphID), theme);

		echartLine.setOption({
			title: {
				text: 'Requests'
			},
			tooltip: {
				trigger: 'axis'
			},
			legend: {
				x: 220,
				y: 40,
				data: env.servicesNames
			},
			toolbox: {
				show: true,
				feature: {
					magicType: {
						show: true,
						title: {
							line: 'Line',
							bar: 'Bar',
							stack: 'Stack',
							tiled: 'Tiled'
						},
						type: ['line', 'bar', 'stack', 'tiled']
					},
					saveAsImage: {
						show: true,
						title: "Save Image"
					}
				}
			},
			calculable: true,
			xAxis: [{
				type: 'category',
				boundaryGap: false,
				data: lineInfo.legend
			}],
			yAxis: [{
				type: 'value'
			}],
			series: lineData
		});
	}
}