$(function() {
    "use strict";


    // chart1 - Performance
    // Parse the dynamic data from the Django context
    var chartDataElementTopJournals = document.getElementById('chart1');
    var performanceDataTopJournals = JSON.parse(chartDataElementTopJournals.getAttribute('data-performance'));

    // Extract years, publicationsData, and citationsData from the parsed data
    var journalNames = performanceDataTopJournals.map(function(entry) {
        return entry.journal;
    });

    var publicationsDataTopJournals = performanceDataTopJournals.map(function(entry) {
        return entry.total_publications;
    });

    var citationsDataTopJournals = performanceDataTopJournals.map(function(entry) {
        return entry.total_citations;
    });

    //     console.log(performanceDataTopJournals);
    // console.log(publicationsDataTopJournals);
    // console.log(citationsDataTopJournals);

    var ctx = document.getElementById('chart1').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: journalNames.slice(1),
            datasets: [{
                    label: 'Publications',

                    data: publicationsDataTopJournals.slice(1),
                    backgroundColor: [
                        "#fff"
                    ],
                    borderColor: [
                        "#fff"
                    ],
                    borderWidth: 0,
                    borderRadius: 20
                },
                {
                    label: 'Citations',
                    data: citationsDataTopJournals.slice(1),
                    backgroundColor: [
                        "rgb(255 255 255 / 50%)"
                    ],
                    borderColor: [
                        "rgb(255 255 255 / 50%)"
                    ],
                    borderWidth: 0,
                    borderRadius: 20
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            barPercentage: 0.7,
            categoryPercentage: 0.45,
            plugins: {
                legend: {
                    position: 'bottom',
                    display: true,
                    labels: {
                        color: 'rgb(255 255 255 / 75%)'
                    }

                }
            },
            scales: {
                x: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                        display: false
                    },
                    grid: {
                        display: false,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                    },
                    grid: {
                        display: true,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },

            }
        }
    });


     // Parse the dynamic data from the Django context
     var chartDataElement = document.getElementById('chart3YearsPerformance');
     console.log(chartDataElement.getAttribute('data-performance'))
     var performanceData = JSON.parse(chartDataElement.getAttribute('data-performance'));
 
     // Extract years, publicationsData, and citationsData from the parsed data
     var years = performanceData.map(function(entry) {
         return entry.year;
     });
 
     var publicationsData = performanceData.map(function(entry) {
         return entry.total_publications;
     });
 
     var citationsData = performanceData.map(function(entry) {
         return entry.total_citations;
     });
    // 3 years Performance
    var ctx = document.getElementById('chart3YearsPerformance').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [{
                    label: 'Publications',

                    data: publicationsData,
                    backgroundColor: [
                        "#fff"
                    ],
                    borderColor: [
                        "#fff"
                    ],
                    borderWidth: 0,
                    borderRadius: 20
                },
                {
                    label: 'Citations',
                    data: citationsData,
                    backgroundColor: [
                        "rgb(255 255 255 / 50%)"
                    ],
                    borderColor: [
                        "rgb(255 255 255 / 50%)"
                    ],
                    borderWidth: 0,
                    borderRadius: 20
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            barPercentage: 0.7,
            categoryPercentage: 0.45,
            plugins: {
                legend: {
                    position: 'top',
                    display: true,
                    labels: {
                        color: 'rgb(255 255 255 / 75%)'
                    }

                }
            },
            scales: {
                x: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                    },
                    grid: {
                        display: true,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                    },
                    grid: {
                        display: true,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },

            }
        }
    });



    // chart2 - Schools publications
    // Parse the dynamic data from the Django context
    var chartDataElementTopSchools = document.getElementById('chart2');
    var performanceDataTopSchools = JSON.parse(chartDataElementTopSchools.getAttribute('data-performance'));

    // Extract years, publicationsData, and citationsData from the parsed data
    var schoolNames = performanceDataTopSchools.map(function(entry) {
        return entry.school;
    });

    var publicationsDataSchools = performanceDataTopSchools.map(function(entry) {
        return entry.total_publications;
    });

    var ctx = document.getElementById('chart2').getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: schoolNames,
            datasets: [{
                data: publicationsDataSchools,
                backgroundColor: [
                    "rgb(255 255 255 / 100%)",
                    "rgb(255 255 255 / 50%)",
                    "rgb(255 255 255 / 25%)"
                ],
                borderWidth: 0
            }]
        },
        options: {
            maintainAspectRatio: false,
            cutout: 110,
            plugins: {
                legend: {
                    display: false,
                }
            }

        }
    });


    // 7 Years Performance Graph - chart3
    // Parse the dynamic data from the Django context
    var chartDataElement10Years = document.getElementById('chart3');
    var performanceData10Years = JSON.parse(chartDataElement10Years.getAttribute('data-performance'));

    // Extract years, publicationsData, and citationsData from the parsed data
    var years10Years = performanceData10Years.map(function(entry) {
        return entry.year;
    });

    var publicationsData10Years = performanceData10Years.map(function(entry) {
        return entry.total_publications;
    });

    var citationsData10Years = performanceData10Years.map(function(entry) {
        return entry.total_citations;
    });

    var ctx = document.getElementById('chart3').getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years10Years,
            datasets: [{
                label: 'Publications',
                data: publicationsData10Years,
                backgroundColor: [
                    "rgb(255 255 255 / 100%)",
                ],
                fill: {
                    target: 'origin',
                    above: 'rgb(255 255 255 / 12%)', // Area will be red above the origin
                    below: 'rgb(255 255 255 / 12%)' // And blue below the origin
                },
                tension: 0.4,
                borderColor: [
                    "rgb(255 255 255 / 100%)",
                ],
                borderWidth: 4
            },{
                label: 'Citations',
                data: citationsData10Years,
                backgroundColor: [
                    "rgb(255 255 255 /50%)",
                ],
                fill: {
                    target: 'origin',
                    above: 'rgb(255 255 255 / 20%)', // Area will be red above the origin
                    below: 'rgb(255 255 255 / 20%)' // And blue below the origin
                },
                tension: 0.4,
                borderColor: [
                    "rgb(255 255 255 /50%)",
                ],
                borderWidth: 4
            }, ]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                }
            },
            scales: {
                x: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                    },
                    grid: {
                        display: true,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    ticks: {
                        color: "rgb(255 255 255 / 75%)", // this here
                    },
                    grid: {
                        display: true,
                        color: "rgba(221, 221, 221, 0.08)"
                    }
                },

            }
        }
    });



    //donut

    $("span.donut").peity("donut", {
        width: 130,
        height: 130
    });


});