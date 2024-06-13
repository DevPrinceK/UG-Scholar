$(function () {
    "use strict";

    var options = {
        chart: {
          type: 'bar',
          height: 350
        },
        series: [{
          name: 'Thematic Areas',
          data: [30, 40, 35, 50] // Sample data
        }],
        xaxis: {
          categories: ['Theme 1', 'Theme 2', 'Theme 3', 'Theme 4']
        },
        title: {
          text: 'Column Chart with ApexCharts',
          align: 'left',
          style: {
            fontSize: '18px',
            color: '#666'
          }
        },
        colors: ['#1E90FF', '#32CD32', '#FF4500', '#FFD700']
      };
    
      var chart = new ApexCharts(document.querySelector("#apexChart"), options);
      chart.render();
    

});




// $(function () {
//     "use strict";


//     // // chart 13
//     //  // Parse the dynamic data from the Django context
//     //  var college_breakdown_canvas = document.getElementById('chart13');
//     //  var college_breakdown_data = JSON.parse(college_breakdown_canvas.getAttribute('data-performance'));
 
//     //  // Extract college names and total publications from the data
//     // var college_publication_data = college_breakdown_data.map(function (item) {
//     //     return {
//     //         name: item.college,
//     //         y: item.total_publications,
//     //         drilldown: item.college
//     //     };
//     // });

//     // NOTE: REMOVE THIS LATER
//     var thematic_data = [
//         {
//             name: "Agriculture",
//             y: 10,
//             drilldown: "Agriculture"
//         },
//         {
//             name: "Engineering",
//             y: 20,
//             drilldown: "Engineering"
//         },
//         {
//             name: "Health Sciences",
//             y: 30,
//             drilldown: "Health Sciences"
//         },
//         {
//             name: "Humanities",
//             y: 40,
//             drilldown: "Humanities"
//         },
//         {
//             name: "Law",
//             y: 50,
//             drilldown: "Law"
//         },
//         {
//             name: "Natural Sciences",
//             y: 60,
//             drilldown: "Natural Sciences"
//         },
//         {
//             name: "Social Sciences",
//             y: 70,
//             drilldown: "Social Sciences"
//         },
//     ]


//         // Create the chart
//         Highcharts.chart('thematic-chart', {
//             chart: {
//                 height: 360,
//                 type: 'column',
//                 styledMode: true
//             },
//             credits: {
//                 enabled: false
//             },
//             title: {
//                 text: 'Research Thematic Areas'
//             },
//             accessibility: {
//                 announceNewData: {
//                     enabled: true
//                 }
//             },
//             xAxis: {
//                 type: 'category'
//             },
//             yAxis: {
//                 title: {
//                     text: 'Total Publications'
//                 }
//             },
//             legend: {
//                 enabled: false
//             },
//             plotOptions: {
//                 series: {
//                     borderWidth: 0,
//                     dataLabels: {
//                         enabled: true,
//                         format: '{point.y}'
//                     }
//                 }
//             },
//             tooltip: {
//                 headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
//                 pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> of total<br/>'
//             },
//             series: [{
//                 name: "Publications",
//                 colorByPoint: true,
//                 data:thematic_data,
//             }],
    
//         });
    

// });