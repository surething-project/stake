$(function(){
    $(document).ready(function(){
        // start up the SocketIO connection to the server    
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        //console.log("I've been called, SOCKET");
        var table = $('#short_traffic_table').DataTable({
            headers: ['timestamp','src_device_name','dst_device_name','IP_src','IP_dst','ETH_src','ETH_dst','IP_p'],
            columns: [
            { title: "Timestamp",data: "timestamp" },
            { title: "Source Device Name",data: "src_device_name" },
            { title: "Dest. Device Name",data: "dst_device_name" },
            { title:'Source IP',data: "IP_src" },
            { title: "Destination IP",data: "IP_dst" },
            { title:'Source MAC Address',data: "ETH_src" },
            { title:'Dest. MAC Address',data: "ETH_dst" }//,
            //{ title: "Prot.",data: "IP_p" }                    
            ],
            pageLength: 5
        });
        socket.on('table', function(msg) {
            var loading =  document.getElementById('short_loading_table');
            if (typeof(loading) != 'undefined' && loading != null)
            {
                loading.remove();
            }
            table.clear().rows.add(msg).draw(false);
            //console.log(msg)
            console.log("Table updated");          
        });
        $('#alerttable_short').dataTable({
                "autoWidth": false,
                "lengthChange": false,
                "pageLength": 5
               // ,"order": [[6, 'desc']]
               ,columns: [
                {data: "TIMESTAMP"},
                {data: "ALERT_TYPE"},
                {data: "TITLE"},
                {data: "SHORT_DESCRIPTION"}
              ]
        });
    });
});

