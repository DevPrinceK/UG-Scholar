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

    var seriesData = (Array.isArray(parsed) && parsed.length)
        ? parsed.map(function (d) {
            return {
                name: d.name || d.label || d.theme || 'Item',
                y: typeof d.y === 'number' ? d.y :
                   typeof d.value === 'number' ? d.value :
                   typeof d.count === 'number' ? d.count : 0
            };
        })
        : [
            { name: "Agriculture", y: 10 },
            { name: "Engineering", y: 20 },
            { name: "Health Sciences", y: 30 },
            { name: "Humanities", y: 40 },
            { name: "Law", y: 50 },
            { name: "Natural Sciences", y: 60 },
            { name: "Social Sciences", y: 70 }
        ];

    Highcharts.chart('thematic-chart', {
        chart: {
            height: 360,
            type: 'column'
        },
        credits: { enabled: false },
        title: { text: 'Research Thematic Areas' },
        xAxis: { type: 'category' },
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