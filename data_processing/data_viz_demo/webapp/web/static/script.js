
function refreshClicked(){
    let desired_data = document.getElementById("datasets").value;
    render_chart('A', `${desired_data} data`, desired_data)
}

function render_chart(dataset='A', title='Soil Data', data_type='soil') {
    let response = `http://127.0.0.1:5000/api/get_chart_data?data_type=${data_type}`
    Highcharts.getJSON(
        response,
        function (response) {
            console.log(response)
            Highcharts.chart('container', {
                chart: {
                    zoomType: 'x'
                },
                title: {
                    text: title
                },
                subtitle: {
                    text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
                },
                xAxis: {
                    type: 'datetime',
                    title: {
                        text: 'Time'
                    }
                    //min: response.xmin
                },
                yAxis: response.yaxes,
                    /*{
                    title: {
                        text: 'hi'
                    }
                },*/
                legend: {
                    enabled: true
                },
                plotOptions: {
                    area: {
                        fillColor: {
                            linearGradient: {
                                x1: 0,
                                y1: 0,
                                x2: 0,
                                y2: 1
                            },
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                            ]
                        },
                        marker: {
                            radius: 2
                        },
                        lineWidth: 1,
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        },
                        threshold: null
                    }
                },

                series: response.series

                    /*[{
                    type: 'line',
                    name: `${ytitle} over ${xtitle}`,
                    data: data
                }]*/
            });
        }
    );
}

