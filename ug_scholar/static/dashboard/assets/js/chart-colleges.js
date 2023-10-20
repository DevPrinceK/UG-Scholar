$(function () {
    "use strict";


    // chart 13
     // Parse the dynamic data from the Django context
     var college_breakdown_canvas = document.getElementById('chart13');
     var college_breakdown_data = JSON.parse(college_breakdown_canvas.getAttribute('data-performance'));
 
     // Extract college names and total publications from the data
    var college_publication_data = college_breakdown_data.map(function (item) {
        return {
            name: item.college,
            y: item.total_publications,
            drilldown: item.college
        };
    });

 
    // Create the chart
    Highcharts.chart('chart13', {
        chart: {
            height: 360,
            type: 'column',
            styledMode: true
        },
        credits: {
            enabled: false
        },
        title: {
            text: 'College Publications Statistics'
        },
        accessibility: {
            announceNewData: {
                enabled: true
            }
        },
        xAxis: {
            type: 'category'
        },
        yAxis: {
            title: {
                text: 'Total Publications'
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    format: '{point.y}'
                }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> of total<br/>'
        },
        series: [{
            name: "Publications",
            colorByPoint: true,
            data:college_publication_data,
        }],

    });


    // chart 14
     // Extract college names and total publications from the data
     var college_citations_data = college_breakdown_data.map(function (item) {
        return {
            name: item.college,
            y: item.total_citations,
            drilldown: item.college
        };
    });
    // Create the chart
    Highcharts.chart('chart14', {
        chart: {
            height: 360,
            type: 'column',
            styledMode: true
        },
        credits: {
            enabled: false
        },
        title: {
            text: 'College Citations Statistics'
        },
        accessibility: {
            announceNewData: {
                enabled: true
            }
        },
        xAxis: {
            type: 'category'
        },
        yAxis: {
            title: {
                text: 'Total College Citations'
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    format: '{point.y}'
                }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> of total<br/>'
        },
        series: [{
            name: "College Citations",
            colorByPoint: true,
            data: college_citations_data,
        }],

    });


   

});