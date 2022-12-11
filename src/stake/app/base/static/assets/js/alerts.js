$(function(){
        $(document).ready(function(){
            function update_plugin_progress() {
               fetch('/plugins/pluginsprogress').then(response => response.json())  
               .then(json => {
                   //console.log(json);
                   pluginsprogress= "";
                   resultsList= "";
                   for (const [record, plugin] of Object.entries(json)) {
                        //console.log(record, plugin);
                        pluginsprogress +="<div class=\"widget sidebar-alerts alert fade in widget-padding-md border rounded\">"
                        pluginsprogress += "<a href=\"#\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</a>"
                        pluginsprogress += "<p><span class=\"text-white fw-semi-bold\">"+plugin['pluginname']+"</span></p>"
                        pluginsprogress += "<ul>"
                        if(plugin['error']){
                            pluginsprogress += "<li><i class=\"fa fa-circle text-warning\"></i>&nbsp;<span class=\"label-name\">Stand-by A.D.</span></li>"
                        }else{
                            if(plugin['active']){
                                pluginsprogress += "<li><i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"label-name\">Active A.D.</span></li>"
                            }else{
                                pluginsprogress += "<li><i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"label-name\">Inactive A.D.</span></li>"
                            }
                        }
                        if(plugin['retrain']){
                            pluginsprogress += "<li><i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"label-name\">Re-training</span></li>"
                        }else{
                            pluginsprogress += "<li><i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"label-name\">No Re-training</span></li>"
                        }
                        pluginsprogress += "</ul>"
                        pluginsprogress += "<div class=\"progress progress-xs mt-xs mb-0\">"
                        
                        switch(plugin['status']){
                            case "Free":
                                if(plugin['error']){
                                    pluginsprogress += "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                        style=\"width: 100%\"></div>"
                                    pluginsprogress +="</div>"
                                    pluginsprogress +="<small>Error occurred</small>"
                                }else{
                                    pluginsprogress += "<div class=\"progress-bar progress-bar-striped progress-bar-success\"\
                                        style=\"width: 100%\"></div>"
                                    pluginsprogress +="</div>"
                                    pluginsprogress +="<small>Ready 100%</small>"
                                }
                                break;
                            case "ReadingPCAP":
                                pluginsprogress += "<div class=\"progress-bar progress-bar-striped progress-bar-warning\"\
                                    style=\"width: 10%\"></div>"
                                pluginsprogress +="</div>"
                                pluginsprogress +="<small>Reading .pcap 10%</small>"
                                break;
                            case "DataPreProcessing":
                                pluginsprogress += "<div class=\"progress-bar progress-bar-striped progress-bar-info\"\
                                    style=\"width: 80%\"></div>"
                                pluginsprogress +="</div>"
                                pluginsprogress +="<small>Pre-processing data 80%</small>"
                                break;
                            case "PluginEvaluation":
                                pluginsprogress += "<div class=\"progress-bar progress-bar-striped progress-bar-gray-light\"\
                                    style=\"width: 90%\"></div>"
                                pluginsprogress +="</div>"
                                pluginsprogress +="<small>Evaluating Plugin 90%</small>"
                                break;
                            default:
                                pluginsprogress +="</div>"
                                pluginsprogress +="<small>Unknown Status</small>"
                                break;
                        }
                        pluginsprogress +="</div>"

                        resultsList="";
                        plugin_div_id = "plugin_update_"+plugin['pluginname'];
                        plugin_div = document.getElementById(plugin_div_id);
                        if (plugin_div) {
                            //console.log('DIV FOUND '+plugin_div_id)
                            resultsList= resultsList+"<ul><li><h3><header><span class=\"fw-semi-bold\">Plug-in: \'"+plugin['pluginname']+"\' </span>";
                            if (plugin['error']){
                                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-warning\"></i>&nbsp;<span class=\"fw-semi-bold\"> Anomaly Detection in Stand-by </span></small>";
                            }else{
                                if(plugin['active']){
                                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Active Anomaly Detection</span></small>";
                                }else{
                                    resultsList= resultsList+ "<small>&emsp;;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">Inactive Anomaly Detection</span></small>";
                                }
                            }
                            if (plugin['retrain']){
                                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Automatic Re-training</span></small>";

                            }else{
                                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">No Automatic Re-training</span></small>";
                            }
                            resultsList= resultsList+"</header></h3></li></ul>";
                
                            resultsList= resultsList+"<ul><h4><li>"
                            switch(plugin['status']){
                                case "Free":
                                    if(plugin['error']){
                                        resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Error | <span class=\"fw-semi-bold\">Possible solution:</span> Re-train plugin</h4></li> ";
                                        resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                        resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                                                style=\"width: 100%\"></div>";
                                        resultsList= resultsList+"</div></div>";
                                    }else{
                                        resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Free | <span class=\"fw-semi-bold\">Trainining Completed:</span> 100%</h4></li>";
                                        resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                        resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-success\"\
                                                                style=\"width: 100%\"></div>";
                                        resultsList= resultsList+"</div></div>";
                                    }
                                    break;
                                case "ReadingPCAP":
                                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Reading .pcap file | <span class=\"fw-semi-bold\">Currently Trainining:</span> 10%</h4></li>";
                                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-warning\"\
                                                            style=\"width: 10%\"></div>";
                                    resultsList= resultsList+"</div></div>";
                                    break;
                                case "DataPreProcessing":
                                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Pre-processing data | <span class=\"fw-semi-bold\">Currently Trainining:</span> 80%</h4></li>";
                                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-info\"\
                                                            style=\"width: 80%\"></div>";
                                    resultsList= resultsList+"</div></div>";
                                    break;
                                case "PluginEvaluation":
                                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Evaluating Plug-in | <span class=\"fw-semi-bold\">Currently Trainining:</span> 90%</h4></li>";
                                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-gray-light\"\
                                                            style=\"width: 90%\"></div>";
                                    resultsList= resultsList+"</div></div>";
                                    break;
                                default:
                                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Unknown Status</span></h4></li>";
                                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">";
                                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                                            style=\"width: 0%\"></div>";
                                    resultsList= resultsList+"</div></div>";
                                    break;
                                }
                            resultsList= resultsList+"</ul>";
                            plugin_div_id = "#"+plugin_div_id
                            $(plugin_div_id).empty();
                            $(plugin_div_id).append(resultsList);
                        }
                    } 
                    $('#pluginprogress').empty();
                    $('#pluginprogress').append(pluginsprogress);             
                })                           
            }
            update_plugin_progress();
            function update_alert() {
                /*
                <span class="label label-important"><i class="fa fa-bell-o"></i></span>
                <span class="label label-success"><i class="fa fa-tag"></i></span>
                <span class="label label-info"><i class="fa fa-info-circle"></i></span>
                */
               fetch('/alerts/lastalerts').then(response => response.json())  
               .then(json => {
                   //console.log(json);
                   json_object = JSON.parse(json);
                   alert= "";
                   for (const [key, json_data] of Object.entries(json_object)) {
                        //console.log(key, json_data);
                        if (json_data['ALERT_TYPE'] == 'anomaly'){
                            alert = alert+ "<li style=\"background:#a84343;\" role=\"presentation\" class=\"support-ticket\">\
                            <a href=\"#\" class=\"support-ticket\">\
                            <div class=\"picture\"> "
                        }else{
                            alert = alert+ "<li role=\"presentation\" class=\"support-ticket\">\
                            <a href=\"#\" class=\"support-ticket\">\
                            <div class=\"picture\"> "
                        }
                        switch(json_data['ALERT_TYPE']) {
                            case 'info':
                                alert = alert+ "<span class=\"label label-info\"> \
                                <i class=\"fa fa-info-circle\"></i> </span>"  
                              break;
                            case 'success':
                                alert = alert+ "<span class=\"label label-success\"> \
                                <i class=\"fa fa-check-circle\"></i> </span>"   
                              break;
                            case 'error':
                                alert = alert+ "<span class=\"label label-important\"> \
                                <i class=\"fa fa-exclamation-circle\"></i> </span>"    
                                break;
                            case 'anomaly':
                                alert = alert+ "<span class=\"label label-important\"> \
                                <i class=\"fa fa-exclamation\"></i> </span>"   
                                break;
                          }
                        alert = alert+"</div>\
                        <div class=\"details\">\
                        <div class=\"sender\">\
                        "+json_data['TITLE']+"</div> \
                        <div class=\"text\">\
                        "+json_data['SHORT_DESCRIPTION']+"\
                        </div></div></a></li>";
                    }
                    alert = alert+"<li role=\"presentation\"><a href=\"/alerts\" class=\"text-align-center see-all\"> See all alerts \
                        <i class=\"fa fa-arrow-right\"></i></a></li>"
                    $('#alert_nav').empty();
                    $('#alert_nav').append(alert); 
                })                           
            }
            update_alert();
            
            function update_table_alert(row) {
                //console.log('ROW '+row);
                json_object = JSON.parse(row);
                //console.log('CONVERT '+json_object);
                alerttable = document.getElementById('alerttable');
                alerttable_short = document.getElementById('alerttable_short');
                if (alerttable) {
                    alertdatatable = $('#alerttable').DataTable();
                    //alertdatatable.clear();
                    //$('#alerttable').dataTable().fnAddData([json_data]);
                    alertdatatable.rows.add(json_object).draw();
                }
                else if (alerttable_short) {
                    alertdatatable_short = $('#alerttable_short').DataTable();
                    //alertdatatable.clear();
                    //$('#alerttable').dataTable().fnAddData([json_data]);
                    alertdatatable_short.rows.add(json_object).draw();
                }
            }
            // start up the SocketIO connection to the server  
            var socket = io.connect('http://' + document.domain + ':' + location.port);
            // Success Messages
            socket.on('success', function(msg) {
                alert = msg[0];
                update_plugin_progress();
                update_alert();
                Messenger().post({
                    message: alert,
                    type: 'success',
                    showCloseButton: true
                });         
                row = msg[1];
                update_table_alert(row);
            });
            // Error Messages
            socket.on('error', function(msg) {
                alert = msg[0]
                update_plugin_progress();
                update_alert();
                Messenger().post({
                    message: alert,
                    type: 'error',
                    showCloseButton: true
                });         
                row = msg[1];
                update_table_alert(row);
            });
            // Info Messages
            socket.on('info', function(msg) {
                alert = msg[0]
                update_plugin_progress();
                update_alert();
                Messenger().post({
                    message: alert,
                    type: 'info',
                    showCloseButton: true
                });         
                row = msg[1];
                update_table_alert(row);
            });
            // Info Messages
            socket.on('anomaly', function(msg) {
                alert = msg[0]
                update_plugin_progress();
                update_alert();
                Messenger().post({
                    message: alert,
                    type: 'error',
                    showCloseButton: true,
                    actions: {
                        cancel: {
                            label: 'Go to Alerts',
                            action: function() {
                                window.location.replace("/alerts");
                            }
                        }
                    }
                });         
                row = msg[1];
                update_table_alert(row);
            });
        });
        $('.widget').widgster();
        var theme = 'air';
        $.globalMessenger({ theme: theme });
        Messenger.options = { theme: theme  };
        var loc = ['bottom', 'right'];
        //TODO: Change location of alert
        //var $lsel = $('.location-selector');
        var update = function(){
            var classes = 'messenger-fixed';
            for (var i=0; i < loc.length; i++)
                classes += ' messenger-on-' + loc[i];
            $.globalMessenger({ extraClasses: classes, theme: theme  });
            Messenger.options = { extraClasses: classes, theme: theme };
        };
        update();
        /*
        $lsel.locationSelector()
            .on('update', function(pos){
                loc = pos;
                update();
        });
        */  
});