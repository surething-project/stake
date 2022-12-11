
$(function(){
    $(document).ready(function(){
        // start up the SocketIO connection to the server    
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        //console.log("I've been called, SOCKET");
        var table = $('#traffic_table').DataTable({
            headers: ['timestamp','src_device_name','dst_device_name','IP_src','IP_dst','ETH_src','ETH_dst','TCP_dport','TCP_sport','UDP_dport','UDP_sport'],
            columns: [
            { title: "Timestamp",data: "timestamp" },
            { title: "Source Device Name",data: "src_device_name" },
            { title: "Dest. Device Name",data: "dst_device_name" },
            { title:'Source MAC Address',data: "ETH_src" },
            { title:'Dest. MAC Address',data: "ETH_dst" },
            { title:'Source IP',data: "IP_src" },
            { title: "Destination IP",data: "IP_dst" },
           // { title: "Packet length",data: "IP_len" },
           // { title: "IP V." ,data: "IP_v" },
           // { title: "Prot.",data: "IP_p" },
            { title: "TCP Source Port",data: "TCP_sport" },
            {  title: "TCP Dest. Port",data: "TCP_dport" },
            { title: "UDP Source Port",data: "UDP_sport" },
            { title: "UDP Dest. Port",data: "UDP_dport" }                     
            ]
        });
        // this is a callback that triggers when the client is connected
        /*
        socket.on('connect', function() {
            //console.log("I've been called, CONNECT");
            socket.send('[Connection Request]');
        });
        */
        socket.on('table', function(msg) {
                var loading =  document.getElementById('loading-table');
                if (typeof(loading) != 'undefined' && loading != null)
                {
                    loading.remove();
                }
                table.clear().rows.add(msg).draw(false);
                //console.log(msg)
                console.log("Table updated");          
        });
        // Charts [Pie,Donut]
        socket.on('src_ip_pie_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('loading-src-pie');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#src-pie-stats').empty();
            $('#src-pie-stats').append(printArray(json_data));
            new PieChart('#src-pie',getChartData(json_data));
            console.log("Source IP pie chart updated");    
        });
        socket.on('src_mac_pie_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('loading-src-pie2');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#src-pie-stats2').empty();
            $('#src-pie-stats2').append(printArray(json_data));
            new PieChart('#src-pie2',getChartData(json_data));
            console.log("Source MAC pie chart updated");
        });
        socket.on('dst_ip_pie_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('loading-dst-pie');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#dst-pie-stats').empty();
            $('#dst-pie-stats').append(printArray(json_data));
            new PieChart('#dst-pie',getChartData(json_data));
            console.log("Destination IP pie chart updated");  
        });
        socket.on('dst_mac_pie_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('loading-dst-pie2');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#dst-pie-stats2').empty();
            $('#dst-pie-stats2').append(printArray(json_data));
            new PieChart('#dst-pie2',getChartData(json_data));
            console.log("Destination IP pie chart updated");
        });
        socket.on('donut_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('loading-donut');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            new DonutChart('#transport-donut',getChartData(json_data));
            console.log("Transport used donut chart updated");  
        });
        socket.on('src_bar_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('src-loading-bar-chart');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#src-port-stats').empty();
            $('#src-port-stats').append(printArray(json_data));
            new BarChart('#src-port-bar',getChartData2(json_data));
            console.log("Port bar chart updated");  
        });  
        socket.on('dst_bar_chart',function(msg){
            var json_data = JSON.parse(msg);
            var loading =  document.getElementById('dst-loading-bar-chart');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            $('#dst-port-stats').empty();
            $('#dst-port-stats').append(printArray(json_data));
            new BarChart('#dst-port-bar',getChartData2(json_data));
            console.log("Port bar chart updated");  
        }); 
    });

    function printArray(json_data) {
        let array_html = '[';
        let i = 0;
        for(var json_label in json_data){
            if(i==0){
                array_html = array_html +json_label+' ('+json_data[json_label]+')';
                i=i+1;
            }else{
                array_html = array_html + ' | ' +json_label+' ('+json_data[json_label]+')';
            }
        }
        array_html = array_html+']';
        return array_html;
    }
    function getChartData(json_data) {
        let data = [];
        for(var json_label in json_data){
            data.push({
                label: json_label,
                data: json_data[json_label]
            });
        }
        return data;
    }
    function getChartData2(json_data) {
        let data = [];
        let label = [];
        let i = 0;
        for(var json_label in json_data){
            //data.push([ parseInt(json_label), json_data[json_label]]);
            data.push([ i, json_data[json_label]]);
            label.push([(i+0.5),json_label]);
            i=i+1;
        }
        return [label,data];
    }
  
    const COLORS = {
        barChart: ['#22597D', '#2980b9', '#5499c7', '#7fb3d5', '#a9cce3','#d4e6f1','#eaf2f8','#FFFFFF'],
        pieChart: ['#0F2B4A','#174272','#22597D', '#2980b9', '#5499c7', '#7fb3d5', '#a9cce3','#d4e6f1','#eaf2f8','#FFFFFF'],
        donutChart: ['#22597D', '#2980b9', '#5499c7', '#7fb3d5'],
        fontColor: '#c1ccd3',
        gridBorder: 'transparent',
    };
    class PieChart {
        constructor(id,data) {
            //this.$chartContainer = $('#flot-pie');
            this.$chartContainer = $(id);
            this.chart = this.createChart(data);
        }
        createChart(data) {
            let self = this;
            return $.plot(this.$chartContainer, data, {
                series: {
                    pie: {
                        show: true,
                        radius: 1,
                        label: {
                            show: true,
                            radius: 2 / 3,
                            formatter: self.labelFormatter2,
                            threshold: 0.10
                        }
                    }
                },
                grid: {
                    hoverable: true
                },
                legend: {
                    //show: true
                    show: false
                    //,labelFormatter: self.labelFormatter2
                },
                colors: COLORS.pieChart
            });
        }
        labelFormatter(label, series) {
            return `<h1><span class="badge badge-secondary">${label}</span></h1>`;
        }
        labelFormatter2(label, series) {
            return `<h1><span class="badge badge-secondary">${label} (${Math.round(series.percent)}%)</span></h1>`;
        }
    }
    class DonutChart {
        constructor(id,data) {
            this.$chartContainer = $(id);
            this.chart = this.createChart(data); 
        }
        createChart(data) {
            let self = this;
            return $.plot(this.$chartContainer, data, {
                series: {
                    pie: {
                        show: true,
                        innerRadius: 0.5,
                        radius: 1,
                        label: {
                            show: true,
                            radius: 2 / 3,
                            formatter: self.labelFormatter,
                            threshold: 0.10
                        }
                    }
                },
                grid: {
                    hoverable: true
                },
                legend: {
                    show: true,
                    labelFormatter: self.labelFormatter2
                },
                colors: COLORS.donutChart
            });
        }
        labelFormatter(label, series) {
            return `<h1><span class="badge badge-secondary">${label}</span></h1>`;
        }
        labelFormatter2(label, series) {
            return `${label} [${Math.round(series.percent)}%]`;
        }
    }
    class BarChart {
        constructor(id,data) {
            this.$chartContainer = $(id);
            //console.log(data)
            this.chart = this.createChart(data);
        }
        createChart(dataSeries) {
            let self = this;
            return $.plot(this.$chartContainer, [dataSeries[1]], {
                    series: {
                        bars: {
                            show: true,
                            barWidth: 1,
                            label: {
                                show: true,
                                formatter: self.labelFormatter
                            }
                        }
                    },
                    xaxis: {
                        min: 0,
                        ticks: dataSeries[0],
                        axisLabel: 'Port',
                        axisLabelUseCanvas: true,
                        axisLabelFontSizePixels: 13,
                        axisLabelPadding: 15,
                        font: {
                            lineHeight: 13,
                            weight: "bold",
                            color: COLORS.fontColor
                        }
                    },
                    yaxis: {
                        axisLabel: 'Value',
                        axisLabelUseCanvas: true,
                        axisLabelFontSizePixels: 13,
                        axisLabelPadding: 5,
                        font: {
                            lineHeight: 13,
                            weight: "bold",
                            color: COLORS.fontColor
                        }
                    },
                   grid: {
                        hoverable: true,
                        clickable: true,
                        borderWidth: 2
                    },
                    legend: {
                        show: true,
                        labelFormatter:self.labelFormatter2
                    },
                    colors: COLORS.barChart
            });
        }
        labelFormatter(label, series) {
            return `<h1><span class="badge badge-secondary">${label}</span></h1>`;
        }
        labelFormatter2(label, series) {
            return `${label} [${Math.round(series.percent)}%]`;
        }
    }
});
