
$(function(){
    $(document).ready(function(){
        function add_pluginCategory(){
            var e = document.getElementById("add_category");
            var category = e.options[e.selectedIndex].value;
            
            var basic_evaluation_div = document.getElementById("add_basic_evaluation_div");
            var supervised_advanced_evaluation_div = document.getElementById("add_supervised_advanced_evaluation_div");
            var plot_evaluation_div = document.getElementById("add_plot_evaluation_div");
            var testsize_div = document.getElementById("add_testsize_div");
            var testsize_div2 = document.getElementById("add_testsize_div2");
            if (category == 'Supervised') {
                //basic_evaluation_div.style.display = "block";
                //supervised_advanced_evaluation_div.style.display = "block";
                //plot_evaluation_div.style.display = "block";
                testsize_div.style.display = "block";
                testsize_div2.style.display = "block";
            } else {
                //basic_evaluation_div.style.display = "none";
                //supervised_advanced_evaluation_div.style.display = "none";
                //plot_evaluation_div.style.display = "none";
                testsize_div.style.display = "none";
                testsize_div2.style.display = "none";
            }
        }
        function edit_pluginCategory(){
            var e = document.getElementById("edit_category");
            var category = e.options[e.selectedIndex].value;
            
            var basic_evaluation_div = document.getElementById("edit_basic_evaluation_div");
            var supervised_advanced_evaluation_div = document.getElementById("edit_supervised_advanced_evaluation_div");
            var plot_evaluation_div = document.getElementById("edit_plot_evaluation_div");
            var testsize_div = document.getElementById("edit_testsize_div");
            var testsize_div2 = document.getElementById("edit_testsize_div2");
            if (category == 'Supervised') {
                //basic_evaluation_div.style.display = "block";
                //supervised_advanced_evaluation_div.style.display = "block";
                //plot_evaluation_div.style.display = "block";
                testsize_div.style.display = "block";
                testsize_div2.style.display = "block";
            } else {
                //basic_evaluation_div.style.display = "none";
                //supervised_advanced_evaluation_div.style.display = "none";
                //plot_evaluation_div.style.display = "none";
                testsize_div.style.display = "none";
                testsize_div2.style.display = "none";
            }
        }
        function pluginCategory(){
            add_pluginCategory();
            edit_pluginCategory();
        }
        pluginCategory();
        $('#edit_pluginname').change(function() {
            var e = document.getElementById("edit_pluginname");
            var plugin = e.options[e.selectedIndex].value;
            var pluginname = e.options[e.selectedIndex].text;     
            //var plugin = $("#edit_pluginname :selected").val();
            //var pluginname = $("#edit_pluginname :selected").text();
            if (pluginname=='Plug-in Name'){
                console.log('no plugin selected');
                ////Plugin Info
                $('#editpluginform').trigger("reset");
            }else {
                var button = document.getElementById("select_plugin");
                button.click();
            }
        });
        $('#add_ethernet_fields').change(function() {
            var add_ethernet = document.getElementById("add_ethernet_fields").checked
            document.getElementById("add_ETHER_src").checked = add_ethernet
            document.getElementById("add_ETHER_dst").checked = add_ethernet
            document.getElementById("add_ETHER_ip").checked = add_ethernet
            document.getElementById("add_ETHER_type").checked = add_ethernet
        });
        $('#add_arp_fields').change(function() {
            var add_arp = document.getElementById("add_arp_fields").checked
            document.getElementById("add_ARP_hln").checked = add_arp
            document.getElementById("add_ARP_hrd").checked = add_arp
            document.getElementById("add_ARP_op").checked = add_arp
            document.getElementById("add_ARP_pln").checked = add_arp
            document.getElementById("add_ARP_pro").checked = add_arp
            document.getElementById("add_ARP_sha").checked = add_arp
            document.getElementById("add_ARP_spa").checked = add_arp
            document.getElementById("add_ARP_tha").checked = add_arp
            document.getElementById("add_ARP_tpa").checked = add_arp
        });
        $('#add_ip_fields').change(function() {
            var add_ip = document.getElementById("add_ip_fields").checked
            document.getElementById("add_IP_src").checked = add_ip
            document.getElementById("add_IP_dst").checked = add_ip
            document.getElementById("add_IP_df").checked = add_ip
            document.getElementById("add_IP_hl").checked = add_ip
            document.getElementById("add_IP_id").checked = add_ip
            document.getElementById("add_IP_len").checked = add_ip
            document.getElementById("add_IP_mf").checked = add_ip
            document.getElementById("add_IP_off").checked = add_ip
            document.getElementById("add_IP_offset").checked = add_ip
            document.getElementById("add_IP_opts").checked = add_ip
            document.getElementById("add_IP_p").checked = add_ip
            document.getElementById("add_IP_rf").checked = add_ip
            document.getElementById("add_IP_sum").checked = add_ip
            document.getElementById("add_IP_tos").checked = add_ip
            document.getElementById("add_IP_ttl").checked = add_ip
            document.getElementById("add_IP_v").checked = add_ip
        });
        $('#add_icmp_fields').change(function() {
            var add_icmp = document.getElementById("add_icmp_fields").checked
            document.getElementById("add_ICMP_type").checked = add_icmp
            document.getElementById("add_ICMP_code").checked = add_icmp
            document.getElementById("add_ICMP_sum").checked = add_icmp
        });
        $('#add_tcp_fields').change(function() {
            var add_tcp = document.getElementById("add_tcp_fields").checked
            document.getElementById("add_TCP_ack").checked = add_tcp
            document.getElementById("add_TCP_dport").checked = add_tcp
            document.getElementById("add_TCP_sport").checked = add_tcp
            document.getElementById("add_TCP_flags").checked = add_tcp
            document.getElementById("add_TCP_off").checked = add_tcp
            document.getElementById("add_TCP_opts").checked = add_tcp
            document.getElementById("add_TCP_seq").checked = add_tcp
            document.getElementById("add_TCP_sum").checked = add_tcp
            document.getElementById("add_TCP_urp").checked = add_tcp
            document.getElementById("add_TCP_win").checked = add_tcp
        });
        $('#add_udp_fields').change(function() {
            var add_udp = document.getElementById("add_udp_fields").checked
            document.getElementById("add_UDP_dport").checked = add_udp
            document.getElementById("add_UDP_sport").checked = add_udp
            document.getElementById("add_UDP_sum").checked = add_udp
            document.getElementById("add_UDP_ulen").checked = add_udp
        });
        $('#add_payload_fields').change(function() {
            var add_payload = document.getElementById("add_payload_fields").checked
            document.getElementById("add_PAYLOAD_len").checked = add_payload
            document.getElementById("add_PAYLOAD_raw").checked = add_payload
            document.getElementById("add_PAYLOAD_hex").checked = add_payload
        });
        $('#add_extra_fields').change(function() {
            var add_extra = document.getElementById("add_extra_fields").checked
            document.getElementById("add_timestamp").checked = add_extra
        });
        $('#add_basic_evaluation').change(function() {
            var add_basic = document.getElementById("add_basic_evaluation").checked
            document.getElementById("add_accuracy").checked = add_basic
            document.getElementById("add_precision").checked = add_basic
            document.getElementById("add_recall").checked = add_basic
            document.getElementById("add_f_score").checked = add_basic
            document.getElementById("add_specificity").checked = add_basic
            document.getElementById("add_false_positive_rate").checked = add_basic
        });
        $('#add_advanced_evaluation').change(function() {
            var add_advanced = document.getElementById("add_advanced_evaluation").checked
            document.getElementById("add_mahalanobis").checked = add_advanced
            document.getElementById("add_mse").checked = add_advanced
        });
        $('#add_plot_evaluation').change(function() {
            var add_plot = document.getElementById("add_plot_evaluation").checked
            document.getElementById("add_roc").checked = add_plot
        });
//_________________________________________________________________________________________________________________________
        $('#edit_ethernet_fields').change(function() {
            var edit_ethernet = document.getElementById("edit_ethernet_fields").checked
            document.getElementById("edit_ETHER_src").checked = edit_ethernet
            document.getElementById("edit_ETHER_dst").checked = edit_ethernet
            document.getElementById("edit_ETHER_ip").checked = edit_ethernet
            document.getElementById("edit_ETHER_type").checked = edit_ethernet
        });
        $('#edit_arp_fields').change(function() {
            var edit_arp = document.getElementById("edit_arp_fields").checked
            document.getElementById("edit_ARP_hln").checked = edit_arp
            document.getElementById("edit_ARP_hrd").checked = edit_arp
            document.getElementById("edit_ARP_op").checked = edit_arp
            document.getElementById("edit_ARP_pln").checked = edit_arp
            document.getElementById("edit_ARP_pro").checked = edit_arp
            document.getElementById("edit_ARP_sha").checked = edit_arp
            document.getElementById("edit_ARP_spa").checked = edit_arp
            document.getElementById("edit_ARP_tha").checked = edit_arp
            document.getElementById("edit_ARP_tpa").checked = edit_arp
        });
        $('#edit_ip_fields').change(function() {
            var edit_ip = document.getElementById("edit_ip_fields").checked
            document.getElementById("edit_IP_src").checked = edit_ip
            document.getElementById("edit_IP_dst").checked = edit_ip
            document.getElementById("edit_IP_df").checked = edit_ip
            document.getElementById("edit_IP_hl").checked = edit_ip
            document.getElementById("edit_IP_id").checked = edit_ip
            document.getElementById("edit_IP_len").checked = edit_ip
            document.getElementById("edit_IP_mf").checked = edit_ip
            document.getElementById("edit_IP_off").checked = edit_ip
            document.getElementById("edit_IP_offset").checked = edit_ip
            document.getElementById("edit_IP_opts").checked = edit_ip
            document.getElementById("edit_IP_p").checked = edit_ip
            document.getElementById("edit_IP_rf").checked = edit_ip
            document.getElementById("edit_IP_sum").checked = edit_ip
            document.getElementById("edit_IP_tos").checked = edit_ip
            document.getElementById("edit_IP_ttl").checked = edit_ip
            document.getElementById("edit_IP_v").checked = edit_ip
        });
        $('#edit_icmp_fields').change(function() {
            var edit_icmp = document.getElementById("edit_icmp_fields").checked
            document.getElementById("edit_ICMP_type").checked = edit_icmp
            document.getElementById("edit_ICMP_code").checked = edit_icmp
            document.getElementById("edit_ICMP_sum").checked = edit_icmp
        });
        $('#edit_tcp_fields').change(function() {
            var edit_tcp = document.getElementById("edit_tcp_fields").checked
            document.getElementById("edit_TCP_ack").checked = edit_tcp
            document.getElementById("edit_TCP_dport").checked = edit_tcp
            document.getElementById("edit_TCP_sport").checked = edit_tcp
            document.getElementById("edit_TCP_flags").checked = edit_tcp
            document.getElementById("edit_TCP_off").checked = edit_tcp
            document.getElementById("edit_TCP_opts").checked = edit_tcp
            document.getElementById("edit_TCP_seq").checked = edit_tcp
            document.getElementById("edit_TCP_sum").checked = edit_tcp
            document.getElementById("edit_TCP_urp").checked = edit_tcp
            document.getElementById("edit_TCP_win").checked = edit_tcp
        });
        $('#edit_udp_fields').change(function() {
            var edit_udp = document.getElementById("edit_udp_fields").checked
            document.getElementById("edit_UDP_dport").checked = edit_udp
            document.getElementById("edit_UDP_sport").checked = edit_udp
            document.getElementById("edit_UDP_sum").checked = edit_udp
            document.getElementById("edit_UDP_ulen").checked = edit_udp
        });
        $('#edit_payload_fields').change(function() {
            var edit_payload = document.getElementById("edit_payload_fields").checked
            document.getElementById("edit_PAYLOAD_len").checked = edit_payload
            document.getElementById("edit_PAYLOAD_raw").checked = edit_payload
            document.getElementById("edit_PAYLOAD_hex").checked = edit_payload
        });
        $('#edit_extra_fields').change(function() {
            var edit_extra = document.getElementById("edit_extra_fields").checked
            document.getElementById("edit_timestamp").checked = edit_extra
        });
        $('#edit_basic_evaluation').change(function() {
            var edit_basic = document.getElementById("edit_basic_evaluation").checked
            document.getElementById("edit_accuracy").checked = edit_basic
            document.getElementById("edit_precision").checked = edit_basic
            document.getElementById("edit_recall").checked = edit_basic
            document.getElementById("edit_f_score").checked = edit_basic
            document.getElementById("edit_specificity").checked = edit_basic
            document.getElementById("edit_false_positive_rate").checked = edit_basic
        });
        $('#edit_advanced_evaluation').change(function() {
            var edit_advanced = document.getElementById("edit_advanced_evaluation").checked
            document.getElementById("edit_mahalanobis").checked = edit_advanced
            document.getElementById("edit_mse").checked = edit_advanced
        });
        $('#edit_plot_evaluation').change(function() {
            var edit_plot = document.getElementById("edit_plot_evaluation").checked
            document.getElementById("edit_roc").checked = edit_plot
        });
        $('#add_category').change(function() {
            add_pluginCategory();
        });
        $('#edit_category').change(function() {
            edit_pluginCategory();
        });
    });
});