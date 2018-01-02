$(document).ready(function(){

    $('#row-tile-0').show();
    $('#version-action-0').show();
    $('#version-files-0').show();

    $(".select2_single").select2({
         placeholder: "Select a file",
        allowClear: true
    });

  var theme = {
    color: [
        '#26B99A', '#34495E', '#BDC3C7', '#3498DB',
        '#9B59B6', '#8abb6f', '#759c6a', '#bfd3b7'
    ],

    title: {
        itemGap: 8,
        textStyle: {
            fontWeight: 'normal',
            color: '#408829'
        }
    },

    dataRange: {
        color: ['#1f610a', '#97b58d']
    },

    toolbox: {
        color: ['#408829', '#408829', '#408829', '#408829']
    },

    tooltip: {
        backgroundColor: 'rgba(0,0,0,0.5)',
        axisPointer: {
            type: 'line',
            lineStyle: {
                color: '#408829',
                type: 'dashed'
            },
            crossStyle: {
                color: '#408829'
            },
            shadowStyle: {
                color: 'rgba(200,200,200,0.3)'
            }
        }
    },

    dataZoom: {
        dataBackgroundColor: '#eee',
        fillerColor: 'rgba(64,136,41,0.2)',
        handleColor: '#408829'
    },
    grid: {
        borderWidth: 0
    },

    categoryAxis: {
        axisLine: {
            lineStyle: {
                color: '#408829'
            }
        },
        splitLine: {
            lineStyle: {
                color: ['#eee']
            }
        }
    },

    valueAxis: {
        axisLine: {
            lineStyle: {
                color: '#408829'
            }
        },
        splitArea: {
            show: true,
            areaStyle: {
                color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)']
            }
        },
        splitLine: {
            lineStyle: {
                color: ['#eee']
            }
        }
    },
    timeline: {
        lineStyle: {
            color: '#408829'
        },
        controlStyle: {
            normal: {color: '#408829'},
            emphasis: {color: '#408829'}
        }
    },

    k: {
        itemStyle: {
            normal: {
                color: '#68a54a',
                color0: '#a9cba2',
                lineStyle: {
                    width: 1,
                    color: '#408829',
                    color0: '#86b379'
                }
            }
        }
    },
    map: {
        itemStyle: {
            normal: {
                areaStyle: {
                    color: '#ddd'
                },
                label: {
                    textStyle: {
                        color: '#c12e34'
                    }
                }
            },
            emphasis: {
                areaStyle: {
                    color: '#99d2dd'
                },
                label: {
                    textStyle: {
                        color: '#c12e34'
                    }
                }
            }
        }
    },
    force: {
        itemStyle: {
            normal: {
                linkStyle: {
                    strokeColor: '#408829'
                }
            }
        }
    },
    chord: {
        padding: 4,
        itemStyle: {
            normal: {
                lineStyle: {
                    width: 1,
                    color: 'rgba(128, 128, 128, 0.5)'
                },
                chordStyle: {
                    lineStyle: {
                        width: 1,
                        color: 'rgba(128, 128, 128, 0.5)'
                    }
                }
            },
            emphasis: {
                lineStyle: {
                    width: 1,
                    color: 'rgba(128, 128, 128, 0.5)'
                },
                chordStyle: {
                    lineStyle: {
                        width: 1,
                        color: 'rgba(128, 128, 128, 0.5)'
                    }
                }
            }
        }
    },
    gauge: {
        startAngle: 225,
        endAngle: -45,
        axisLine: {
            show: true,
            lineStyle: {
                color: [[0.2, '#86b379'], [0.8, '#68a54a'], [1, '#408829']],
                width: 8
            }
        },
        axisTick: {
            splitNumber: 10,
            length: 12,
            lineStyle: {
                color: 'auto'
            }
        },
        axisLabel: {
            textStyle: {
                color: 'auto'
            }
        },
        splitLine: {
            length: 18,
            lineStyle: {
                color: 'auto'
            }
        },
        pointer: {
            length: '90%',
            color: 'auto'
        },
        title: {
            textStyle: {
                color: '#333'
            }
        },
        detail: {
            textStyle: {
                color: 'auto'
            }
        }
    },
    textStyle: {
        fontFamily: 'Arial, Verdana, sans-serif'
    }
  };
    
    var echartLine = echarts.init(document.getElementById('echart_line'), theme);
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                var response = JSON.parse( xhttp.responseText );


                var legend_data = [];
                var data_array = [];
                for( var key in response.versions){
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
                        data: response.versions[key]
                    };
                    legend_data.push( key );
                    data_array.push( data_point );
                }

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
                      data: response.xAxis
                    }],
                    yAxis: [{
                      type: 'value'
                    }],
                    series: data_array
                });
            }
        };
        xhttp.open("GET", "/AJAX" + window.location.pathname, true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send();
});

function version_switch( number, current, next ){

    $("#row-tile-" + current.toString()).hide();
    $("#modal-" + current.toString()).modal('toggle');
    $("#row-tile-" + next.toString()).show();

    $('#version-action-' + current.toString()).hide();
    $('#version-action-' + next.toString()).show();

    $('#version-files-' + current.toString()).hide();
    $('#version-files-' + next.toString()).show();
}

function promote_service( sid, eid ){
    alert(" You are promoting");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse( xhttp.responseText );
            var alert_message = new PNotify({
                title: response.title,
                text: response.content,
                type: response.type,
                styling: 'bootstrap3'
            });

            $('body').append(alert_message);

            if( response.type == "success"){
                alert( "Got here" );
            }
        }
    };
    xhttp.open("POST", "/AJAX/deploy_service.py", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var msg = "eid=" + eid;
    msg = msg + "&sid=" + sid;
    xhttp.send( msg );
}

function activate_service( sid, eid ){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse( xhttp.responseText );
            var alert_message = new PNotify({
                title: response.title,
                text: response.content,
                type: response.type,
                styling: 'bootstrap3'
            });

            $('body').append(alert_message);

            if( response.type == "success"){
                tag = "-" + eid.toString();
                $('#button-a' + tag).hide();
                $('#button-d' + tag).show();
                $('#status' + tag).html( "<strong>ACTIVE</strong>" );
            }
        }
    };
    xhttp.open("POST", "/AJAX/activate_service.py", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var msg = "eid=" + eid;
    msg = msg + "&sid=" + sid;
    xhttp.send( msg );
}

function deactivate_service( sid, eid ){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse( xhttp.responseText );
            var alert_message = new PNotify({
                title: response.title,
                text: response.content,
                type: response.type,
                styling: 'bootstrap3'
            });

            $('body').append(alert_message);

            if( response.type == "success"){
                tag = "-" + eid.toString();
                $('#button-d' + tag).hide();
                $('#button-a' + tag).show();
                $('#status' + tag).html( "<strong>INACTIVE</strong>" );
            }
        }
    };
    xhttp.open("POST", "/AJAX/deactivate_service.py", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var msg = "eid=" + eid;
    msg = msg + "&sid=" + sid;
    xhttp.send( msg );
}