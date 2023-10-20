$(function() {
    "use strict";

    
    // Parse the dynamic data from the Django context
    var institution_indexes_canvas = document.getElementById('indexesChart');
    var institution_indexes_data = JSON.parse(institution_indexes_canvas.getAttribute('data-performance'));

    // Extract institution names and total publications from the data
    var institution_publication_data = institution_indexes_data.map(function (item) {
        return {
            name: item.name,
            y: item.index,
            drilldown: item.name
        };
    });

    // Create the chart
    Highcharts.chart('indexesChart', {
        chart: {
            height: 360,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Institute/Center Indexes Statistics'
        },
        tooltip: {
            pointFormat: '{series.name}: <p>{point.percentage:.1f}%</p>'
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<p>{point.name}</p>: {point.percentage:.1f} %',
                    connectorColor: 'silver'
                }
            }
        },
        series: [{
            name: 'Indexes',
            data: institution_publication_data
        }]
    });


    // Parse the dynamic data from the Django context
    var author_and_pub_canvas = document.getElementById('authorNPubChart');
    var author_and_pub_data = JSON.parse(author_and_pub_canvas.getAttribute('data-performance'));

    // Extract institution names and total publications from the data
    var institution_auth_pub = author_and_pub_data.map(function (item) {
        return {
            name: item.name,
            y: item.index,
            drilldown: item.name
        };
    });

    // Create the chart
    Highcharts.chart('authorNPubChart', {
        chart: {
            height: 360,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Institute/Center Authors and Publications'
        },
        tooltip: {
            pointFormat: '{series.name}: <p>{point.percentage:.1f}%</p>'
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<p>{point.name}</p>: {point.percentage:.1f} %',
                    connectorColor: 'silver'
                }
            }
        },
        series: [{
            name: 'Count',
            data: institution_auth_pub
        }]
    });


});
