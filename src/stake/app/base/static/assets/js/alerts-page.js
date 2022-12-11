$(function(){
    $(document).ready(function(){
        $('#alerttable').dataTable({
            "autoWidth": false,
            "lengthChange": false,
            "pageLength": 25
           // ,"order": [[6, 'desc']]
           ,columns: [
            {data: "TIMESTAMP"},
            {data: "CONTEXT"},
            {data: "ALERT_TYPE"},
            {data: "TITLE"},
            {data: "SHORT_DESCRIPTION"},
            {data: "DESCRIPTION"}
          ]
          /*,'rowCallback': function(row, data, index){
                if(data[2] == "anomaly"){
                    $(row).css('background-color', 'red');
                }
                else if(data[3] == 'info'){
                    $(row).css('background-color', 'blue');
                }
                else if(data[4] == 'success'){
                    $(row).css('background-color', 'green');
                }
                else if(data[1] == 'success'){
                    $(row).css('background-color', 'green');
                }
          }*/
        });
    });    
});