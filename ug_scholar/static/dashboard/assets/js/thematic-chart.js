$(function () {
    "use strict";

    var container = document.getElementById('thematic-chart');
    if (!container) return;

    // Try to read dynamic data from the element's data attribute
    var raw = container.getAttribute('data-performance') || '';
    var parsed = [];
    try {
        parsed = raw ? JSON.parse(raw) : [];
    } catch (e) {
        // Ignore JSON parse errors and fall back to demo data
        parsed = [];
    }

    var seriesData = Array.isArray(parsed)
        ? parsed.map(function (d) {
            return {
                name: d.name || d.label || d.theme || 'Item',
                y: typeof d.y === 'number' ? d.y :
                   typeof d.value === 'number' ? d.value :
                   typeof d.count === 'number' ? d.count : 0
            };
        })
        : [];

    Highcharts.chart('thematic-chart', {
        chart: {
            height: 360,
            type: 'column'
        },
        credits: { enabled: false },
        title: {
            text: seriesData.length ? 'Research Thematic Areas' : 'No classified publications yet'
        },
        xAxis: {
            type: 'category',
            labels: {
                rotation: -35,
                style: { fontSize: '11px' }
            }
        },
        yAxis: { title: { text: 'Total Publications' } },
        legend: { enabled: false },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: { enabled: true, format: '{point.y}' }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b><br/>'
        },
        series: [{
            name: 'Publications',
            colorByPoint: true,
            data: seriesData
        }]
    });
});
