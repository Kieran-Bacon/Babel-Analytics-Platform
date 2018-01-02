
$(document).ready(function() {
  //define chart clolors ( you maybe add more colors if you want or flot will add it automatic )
  var chartColours = ['#96CA59', '#3F97EB', '#72c380', '#6f7a8a', '#f7cb38', '#5a8022', '#2c7282'];

  //generate random number for charts
  randNum = function() {
    return (Math.floor(Math.random() * (1 + 40 - 20))) + 20;
  };

  var d1 = [];
  //var d2 = [];

  //here we generate data for chart
  for (var i = 0; i < 30; i++) {
    d1.push([new Date(Date.today().add(i).days()).getTime(), randNum() + i + i + 10]);
    //    d2.push([new Date(Date.today().add(i).days()).getTime(), randNum()]);
  }

  var chartMinDate = d1[0][0]; //first day
  var chartMaxDate = d1[20][0]; //last day

  var tickSize = [1, "day"];
  var tformat = "%d/%m/%y";

  //graph options
  var options = {
    grid: {
      show: true,
      aboveData: true,
      color: "#3f3f3f",
      labelMargin: 10,
      axisMargin: 0,
      borderWidth: 0,
      borderColor: null,
      minBorderMargin: 5,
      clickable: true,
      hoverable: true,
      autoHighlight: true,
      mouseActiveRadius: 100
    },
    series: {
      lines: {
        show: true,
        fill: true,
        lineWidth: 2,
        steps: false
      },
      points: {
        show: true,
        radius: 4.5,
        symbol: "circle",
        lineWidth: 3.0
      }
    },
    legend: {
      position: "ne",
      margin: [0, -25],
      noColumns: 0,
      labelBoxBorderColor: null,
      labelFormatter: function(label, series) {
        // just add some space to labes
        return label + '&nbsp;&nbsp;';
      },
      width: 40,
      height: 1
    },
    colors: chartColours,
    shadowSize: 0,
    tooltip: true, //activate tooltip
    tooltipOpts: {
      content: "%s: %y.0",
      xDateFormat: "%d/%m",
      shifts: {
        x: -30,
        y: -50
      },
      defaultTheme: false
    },
    yaxis: {
      min: 0
    },
    xaxis: {
      mode: "time",
      minTickSize: tickSize,
      timeformat: tformat,
      min: chartMinDate,
      max: chartMaxDate
    }
  };
  var plot = $.plot($("#placeholder33x"), [{
    data: d1,
    lines: {
      fillColor: "rgba(150, 202, 89, 0.12)"
    }, //#96CA59 rgba(150, 202, 89, 0.42)
    points: {
      fillColor: "#fff"
    }
  }], options);
});

$(document).ready(function(){
  var options = {
    legend: false,
    responsive: false
  };

  new Chart(document.getElementById("canvas1"), {
    type: 'doughnut',
    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
    data: {
      labels: [
      "Symbian",
      "Blackberry",
      "Other",
      "Android",
      "IOS"
      ],
      datasets: [{
        data: [15, 20, 30, 10, 30],
        backgroundColor: [
        "#BDC3C7",
        "#9B59B6",
        "#E74C3C",
        "#26B99A",
        "#3498DB"
        ],
        hoverBackgroundColor: [
        "#CFD4D8",
        "#B370CF",
        "#E95E4F",
        "#36CAAB",
        "#49A9EA"
        ]
      }]
    },
    options: options
  });
});

$(document).ready(function() {

  var cb = function(start, end, label) {
    console.log(start.toISOString(), end.toISOString(), label);
    $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
  };

  var optionSet1 = {
    startDate: moment().subtract(29, 'days'),
    endDate: moment(),
    minDate: '01/01/2012',
    maxDate: '12/31/2015',
    dateLimit: {
      days: 60
    },
    showDropdowns: true,
    showWeekNumbers: true,
    timePicker: false,
    timePickerIncrement: 1,
    timePicker12Hour: true,
    ranges: {
      'Today': [moment(), moment()],
      'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
      'Last 7 Days': [moment().subtract(6, 'days'), moment()],
      'Last 30 Days': [moment().subtract(29, 'days'), moment()],
      'This Month': [moment().startOf('month'), moment().endOf('month')],
      'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    },
    opens: 'left',
    buttonClasses: ['btn btn-default'],
    applyClass: 'btn-small btn-primary',
    cancelClass: 'btn-small',
    format: 'MM/DD/YYYY',
    separator: ' to ',
    locale: {
      applyLabel: 'Submit',
      cancelLabel: 'Clear',
      fromLabel: 'From',
      toLabel: 'To',
      customRangeLabel: 'Custom',
      daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
      monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
      firstDay: 1
    }
  };
  $('#reportrange span').html(moment().subtract(29, 'days').format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
  $('#reportrange').daterangepicker(optionSet1, cb);
  $('#reportrange').on('show.daterangepicker', function() {
    console.log("show event fired");
  });
  $('#reportrange').on('hide.daterangepicker', function() {
    console.log("hide event fired");
  });
  $('#reportrange').on('apply.daterangepicker', function(ev, picker) {
    console.log("apply event fired, start/end dates are " + picker.startDate.format('MMMM D, YYYY') + " to " + picker.endDate.format('MMMM D, YYYY'));
  });
  $('#reportrange').on('cancel.daterangepicker', function(ev, picker) {
    console.log("cancel event fired");
  });
  $('#options1').click(function() {
    $('#reportrange').data('daterangepicker').setOptions(optionSet1, cb);
  });
  $('#options2').click(function() {
    $('#reportrange').data('daterangepicker').setOptions(optionSet2, cb);
  });
  $('#destroy').click(function() {
    $('#reportrange').data('daterangepicker').remove();
  });
});