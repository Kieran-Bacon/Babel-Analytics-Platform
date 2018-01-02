$(document).ready(function(){
	servicesRequestData();
	servicesCPUData();

	serverCharacteristics();

	Morris.Bar({
          element: 'graph_bar_group',
          data: [
            {"period": "2016-10-01", "licensed": 807, "sorned": 660},
            {"period": "2016-09-30", "licensed": 1251, "sorned": 729},
            {"period": "2016-09-29", "licensed": 1769, "sorned": 1018},
            {"period": "2016-09-20", "licensed": 2246, "sorned": 1461},
            {"period": "2016-09-19", "licensed": 2657, "sorned": 1967},
            {"period": "2016-09-18", "licensed": 3148, "sorned": 2627},
            {"period": "2016-09-17", "licensed": 3471, "sorned": 3740},
            {"period": "2016-09-16", "licensed": 2871, "sorned": 2216},
            {"period": "2016-09-15", "licensed": 2401, "sorned": 1656},
            {"period": "2016-09-10", "licensed": 2115, "sorned": 1022}
          ],
          xkey: 'period',
          barColors: ['#26B99A', '#34495E', '#ACADAC', '#3498DB'],
          ykeys: ['licensed', 'sorned'],
          labels: ['Licensed', 'SORN'],
          hideHover: 'auto',
          xLabelAngle: 60,
          resize: true
        });

});

function servicesRequestData(){
	var theme = getTheme();
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var response = JSON.parse( xhttp.responseText );


			var legend_data = [];
			var data_array = [];
			for( var key in response.services){
				var data_point = {
					name: key,
					type: 'line',
					smooth: true,
					itemStyle: {
						normal: {
							areaStyle: {
								type: 'default'
							}
						}
					},
					data: response.services[key]
				};
				legend_data.push( key );
				data_array.push( data_point );
			}

			var echartLine = echarts.init(document.getElementById('echart_line'), theme);
			echartLine.setOption({
				tooltip: {
					trigger: 'axis'
				},
				legend: {
					x: 220,
					y: 40,
					data: legend_data
				},
				toolbox: {
					show: true,
					x: 'left',
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
					name: 'Dates',
					type: 'category',
					boundaryGap: false,
					data: response.xAxis
				}],
				yAxis: [{
					name: 'Requests',
					type: 'value'
				}],
				series: data_array
			});
		}
	};
	xhttp.open("GET", "/AJAX/SerReq" + window.location.pathname, true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send();
}

function servicesCPUData() {

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var response = JSON.parse( xhttp.responseText );

			Morris.Donut({
				element: 'graph_donut',
				data: response.data,
				colors: ['#26B99A', '#34495E', '#ACADAC', '#3498DB'],
				formatter: function (y) {
					return y + "%";
				},
				resize: true
			});
		}
	};
	xhttp.open("GET", "/AJAX/SerCPU" + window.location.pathname, true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send();

}

function serverCharacteristics() {
	var theme = getTheme();
	var echartRadar = echarts.init(document.getElementById('echart_sonar'), theme);

	echartRadar.setOption({
		tooltip: {
			trigger: 'item'
		},
		legend: {
			orient: 'vertical',
			x: 'right',
			y: 'bottom',
			data: ['Server1', 'Server2']
		},
		polar: [{
			indicator: [{
				text: 'Memory',
				max: 6000
			}, {
				text: 'Cores',
				max: 16000
			}, {
				text: 'Threads',
				max: 30000
			}, {
				text: 'Network',
				max: 38000
			}, {
				text: 'Availabilty',
				max: 52000
			}, {
				text: 'Fault Tolerence',
				max: 25000
			}]
		}],
		calculable: true,
		series: [{
			name: 'Budget vs spending',
			type: 'radar',
			data: [{
				value: [4300, 10000, 28000, 35000, 50000, 19000],
				name: 'Server1'
			}, {
				value: [5000, 14000, 28000, 31000, 42000, 21000],
				name: 'Server2'
			}]
		}]
	});
}