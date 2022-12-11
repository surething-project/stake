from scapy.all import wrpcap
import dpkt, socket, binascii #,gc
import pandas as pd 
import numpy as np
import struct
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from os.path import dirname

def pcap2dataframe(pcap_file_path,maxPackets):  
    print('Starting reading .pcap file...')
    pcapReader = dpkt.pcap.Reader(open(pcap_file_path, "rb"))
    pcapReader = list(reversed(list(pcapReader))) #[:100]
    print('Finished reading .pcap file. \n')

    print('Converting .pcap into dataframe...')    
    ## Collect field names from Eth/IP/TCP/UDP (These will be columns in DF)

    ## ETH available fields:
        #eth_fields = ['data', 'dst', 'get_type', 'get_type_rev', 'ip', 'pack', 'pack_hdr', \
        #  'set_type', 'src', 'type', 'unpack']
    # ETH used fields:
    eth_fields = ['dst', 'src','ip', 'type'] 
    eth_fields = ['ETH_'+x for x in eth_fields]

    ## ARP available fields:
        #arp_fields = ['data', 'hln', 'hrd', 'op', 'pack', 'pack_hdr', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa', 'unpack']
    arp_fields = ['hln', 'hrd', 'op', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa']
    arp_fields = ['ARP_'+x for x in arp_fields]

    ## IP available fields:
        #ip_fields = ['data', 'df', 'dst', 'get_proto', 'hl', 'id', 'len', 'mf', \
        #    'off', 'offset', 'opts', 'p', 'pack', 'pack_hdr', 'rf', 'set_proto', 'src', \
        #        'sum', 'tcp', 'tos', 'ttl', 'unpack', 'v']
    # IP used fields:
    ip_fields = ['df', 'dst', 'hl', 'id', 'len', 'mf', \
        'off', 'offset', 'opts', 'p', 'rf', 'src', \
            'sum', 'tos', 'ttl', 'v']
    ip_fields = ['IP_'+x for x in ip_fields]
    
    ## TCP available fields:
        #tcp_fields = ['ack', 'data', 'dport', 'flags', 'off', 'opts', 'pack', \
        #     'pack_hdr', 'seq', 'sport', 'sum', 'unpack', 'urp', 'win']
    ## TCP used fields:
    tcp_fields = ['ack', 'dport', 'flags', 'off', 'opts', \
          'seq', 'sport', 'sum', 'urp', 'win']
    tcp_fields = ['TCP_'+x for x in tcp_fields]

    ## UDP available fields:
        #udp_fields = ['data', 'dport', 'pack', 'pack_hdr', 'sport', 'sum', 'ulen', 'unpack']
    ## UDP used fields:
    udp_fields = ['dport', 'sport', 'sum', 'ulen']
    udp_fields = ['UDP_'+x for x in udp_fields]

    ## ICMP available fields:
        #icmp_fields = ['code', 'data', 'echo', 'pack', 'pack_hdr', 'sum', 'type', 'unpack']
        #echo_fields = ['data', 'id', 'pack', 'pack_hdr', 'seq', 'unpack']
    icmp_fields = ['code', 'sum', 'type']
    icmp_fields = ['ICMP_'+x for x in icmp_fields]

    ## Payload fields:
    payload_fields = ['PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']

    ## Data in transport layer (TCP/UDP) is added afterwards
    dataframe_fields = ['timestamp'] + eth_fields + arp_fields + ip_fields + icmp_fields + tcp_fields + udp_fields + payload_fields
    
    # Create blank DataFrame
    df = pd.DataFrame(columns=dataframe_fields)
    
    n_packets = 0
    print('Starting iterating packets of the PCAP...')
    for ts, data in pcapReader:
        # Field array for each row of DataFrame
        ether = dpkt.ethernet.Ethernet(data)
        field_values = []
        field_values.append(ts)
        arp = None
        transport = None
        icmp = None
        ## ETHERNET
        for field in eth_fields:
            try:
                field = field.replace("ETH_","")
                if field=='src' or field=='dst':
                    mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", ether[field]))
                    field_values.append(mac_address)
                elif field == 'ip' and hasattr(ether, 'arp'):
                        field_values.append(np.nan)
                elif ether[field]:
                    if isinstance(ether[field],int):
                        field_values.append(ether[field])
                    else:
                        field_values.append(str(ether[field]))
                else:
                    field_values.append(np.nan)
            except:
                pass
        ## ARP:
        if hasattr(ether, 'arp'):
            arp = ether.arp
            for field in arp_fields:
                try:
                    field = field.replace("ARP_","")
                    if field != 'data':
                        if field=='sha' or field=='tha':
                            mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", arp[field]))
                            field_values.append(mac_address)
                        elif field=='spa' or field=='tpa':
                            field_values.append(str(socket.inet_ntoa(arp[field])))
                        elif arp[field]:
                            if isinstance(arp[field],int):
                                field_values.append(arp[field])
                            else:
                                field_values.append(str(binascii.hexlify(arp[field])))
                        else:
                            field_values.append(np.nan)
                except:
                    field_values.append(np.nan)
            dataframe_filling = [np.nan] * (len(ip_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(tcp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(udp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(icmp_fields))
            field_values = field_values + dataframe_filling
        ## IP
        if ether.type == dpkt.ethernet.ETH_TYPE_IP: 
            ip = ether.data
            dataframe_filling = [np.nan] * (len(arp_fields))
            field_values = field_values + dataframe_filling
            # Add all IP fields to dataframe
            for field in ip_fields:
                try:
                    field = field.replace("IP_","")
                    if field == 'opts':
                        field_values.append(len(ip[field]))
                    elif field=='src' or field=='dst':
                        field_values.append(str(socket.inet_ntoa(ip[field])))
                    
                    elif field=='p':
                        if ip[field]==6:
                            field_values.append('TCP')
                        elif ip[field]==17:
                            field_values.append('UDP')
                        elif ip[field]==1:
                            field_values.append('ICMP')
                        else:
                            field_values.append('None')
                    elif ip[field]:
                        if isinstance(ip[field],int):
                            field_values.append(ip[field])
                        else:
                            field_values.append(str(ip[field]))
                    else:
                        field_values.append(np.nan)
                except:
                    pass
            ## ICMP
            if hasattr(ip, 'icmp'):
                icmp = ip.icmp
                for field in icmp_fields:
                    try:
                        field = field.replace("ICMP_","")
                        if field != 'data': 
                            if field == 'code':
                                field_values.append(icmp.code)
                            elif icmp[field]:
                                if isinstance(icmp[field],int):
                                    field_values.append(icmp[field])
                                else:
                                    field_values.append(str(icmp[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                if hasattr(icmp.data, 'ip'):
                    ip = icmp.data.ip
            else:
                dataframe_filling = [np.nan] * (len(icmp_fields))
                field_values = field_values + dataframe_filling
            ## TCP
            if hasattr(ip, 'tcp'):
                transport = ip.tcp
                for field in tcp_fields:
                    try:
                        field = field.replace("TCP_","")
                        if field != 'data':
                            if field == 'opts':
                                field_values.append(len(transport[field]))
                            elif transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
            ## UDP
            elif hasattr(ip, 'udp'):
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                transport = ip.udp
                for field in udp_fields:
                    try:
                        field = field.replace("UDP_","")
                        if field != 'data': 
                            if transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
            ## OTHER PACKETS:
            else:
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
        ## Append transport layer payload
        if transport != None:           
            field_values.append(len(transport['data']))
            field_values.append(str(transport['data']))
            try:
                field_values.append(str(binascii.hexlify(transport['data'])))
            except:
                field_values.append(str(binascii.hexlify(transport['data'].data)))
        elif icmp != None:
            field_values.append(len(icmp['data']))
            field_values.append(str(icmp['data']))
            try:
                field_values.append(str(binascii.hexlify(icmp['data'])))
            except:
                field_values.append(str(repr(icmp['data'].data)))
        elif arp != None:           
            field_values.append(len(arp['data']))
            field_values.append(str(arp['data']))
            try:
                field_values.append(str(binascii.hexlify(arp['data'])))
            except:
                field_values.append(str(binascii.hexlify(arp['data'].data)))
        else:
            continue
        ## Add row to DF
        df_append = pd.DataFrame([field_values], columns=dataframe_fields)
        try:
            df = pd.concat([df, df_append], axis=0)
        except ValueError:
            raise
        n_packets = n_packets+1
            
        if maxPackets == None or maxPackets == 0:
            continue
        elif n_packets >= maxPackets:
            break
    print('Finished iterating packets of the PCAP.')
    print('Total packets read: ',n_packets)
    # Reset Index
    df = df.reset_index()
    # Drop old index column
    df = df.drop(columns="index")
    return df

def packets2dataframe(packets,pcap_file_path):  
    print('Converting captured packets into dataframe...') 
    temp_file_path = dirname(pcap_file_path)
    temp_file_path += '/temp.pcap'
    wrpcap(temp_file_path, packets, append=False)
    pcapReader = dpkt.pcap.Reader(open(temp_file_path, "rb"))
    pcapReader = list(reversed(list(pcapReader)))
    ## Collect field names from Eth/IP/TCP/UDP (These will be columns in DF)

    ## ETH available fields:
        #eth_fields = ['data', 'dst', 'get_type', 'get_type_rev', 'ip', 'pack', 'pack_hdr', \
        #  'set_type', 'src', 'type', 'unpack']
    # ETH used fields:
    eth_fields = ['dst', 'src','ip', 'type'] 
    eth_fields = ['ETH_'+x for x in eth_fields]

    ## ARP available fields:
        #arp_fields = ['data', 'hln', 'hrd', 'op', 'pack', 'pack_hdr', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa', 'unpack']
    arp_fields = ['hln', 'hrd', 'op', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa']
    arp_fields = ['ARP_'+x for x in arp_fields]

    ## IP available fields:
        #ip_fields = ['data', 'df', 'dst', 'get_proto', 'hl', 'id', 'len', 'mf', \
        #    'off', 'offset', 'opts', 'p', 'pack', 'pack_hdr', 'rf', 'set_proto', 'src', \
        #        'sum', 'tcp', 'tos', 'ttl', 'unpack', 'v']
    # IP used fields:
    ip_fields = ['df', 'dst', 'hl', 'id', 'len', 'mf', \
        'off', 'offset', 'opts', 'p', 'rf', 'src', \
            'sum', 'tos', 'ttl', 'v']
    ip_fields = ['IP_'+x for x in ip_fields]
    
    ## TCP available fields:
        #tcp_fields = ['ack', 'data', 'dport', 'flags', 'off', 'opts', 'pack', \
        #     'pack_hdr', 'seq', 'sport', 'sum', 'unpack', 'urp', 'win']
    ## TCP used fields:
    tcp_fields = ['ack', 'dport', 'flags', 'off', 'opts', \
          'seq', 'sport', 'sum', 'urp', 'win']
    tcp_fields = ['TCP_'+x for x in tcp_fields]

    ## UDP available fields:
        #udp_fields = ['data', 'dport', 'pack', 'pack_hdr', 'sport', 'sum', 'ulen', 'unpack']
    ## UDP used fields:
    udp_fields = ['dport', 'sport', 'sum', 'ulen']
    udp_fields = ['UDP_'+x for x in udp_fields]

    ## ICMP available fields:
        #icmp_fields = ['code', 'data', 'echo', 'pack', 'pack_hdr', 'sum', 'type', 'unpack']
        #echo_fields = ['data', 'id', 'pack', 'pack_hdr', 'seq', 'unpack']
    icmp_fields = ['code', 'sum', 'type']
    icmp_fields = ['ICMP_'+x for x in icmp_fields]

    ## Payload fields:
    payload_fields = ['PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']

    ## Data in transport layer (TCP/UDP) is added afterwards
    dataframe_fields = ['timestamp'] + eth_fields + arp_fields + ip_fields + icmp_fields + tcp_fields + udp_fields + payload_fields
    
    # Create blank DataFrame
    df = pd.DataFrame(columns=dataframe_fields)
    
    n_packets = 0
    for ts, data in pcapReader:
        # Field array for each row of DataFrame
        ether = dpkt.ethernet.Ethernet(data)
        field_values = []
        field_values.append(ts)
        arp = None
        transport = None
        icmp = None
        ## ETHERNET
        for field in eth_fields:
            try:
                field = field.replace("ETH_","")
                if field=='src' or field=='dst':
                    mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", ether[field]))
                    field_values.append(mac_address)
                elif field == 'ip' and hasattr(ether, 'arp'):
                        field_values.append(np.nan)
                elif ether[field]:
                    if isinstance(ether[field],int):
                        field_values.append(ether[field])
                    else:
                        field_values.append(str(ether[field]))
                else:
                    field_values.append(np.nan)
            except:
                pass
        ## ARP:
        if hasattr(ether, 'arp'):
            arp = ether.arp
            for field in arp_fields:
                try:
                    field = field.replace("ARP_","")
                    if field != 'data':
                        if field=='sha' or field=='tha':
                            mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", arp[field]))
                            field_values.append(mac_address)
                        elif field=='spa' or field=='tpa':
                            field_values.append(str(socket.inet_ntoa(arp[field])))
                        elif arp[field]:
                            if isinstance(arp[field],int):
                                field_values.append(arp[field])
                            else:
                                field_values.append(str(binascii.hexlify(arp[field])))
                        else:
                            field_values.append(np.nan)
                except:
                    field_values.append(np.nan)
            dataframe_filling = [np.nan] * (len(ip_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(tcp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(udp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(icmp_fields))
            field_values = field_values + dataframe_filling
        ## IP
        if ether.type == dpkt.ethernet.ETH_TYPE_IP: 
            ip = ether.data
            dataframe_filling = [np.nan] * (len(arp_fields))
            field_values = field_values + dataframe_filling
            # Add all IP fields to dataframe
            for field in ip_fields:
                try:
                    field = field.replace("IP_","")
                    if field == 'opts':
                        field_values.append(len(ip[field]))
                    elif field=='src' or field=='dst':
                        field_values.append(str(socket.inet_ntoa(ip[field])))
                    
                    elif field=='p':
                        if ip[field]==6:
                            field_values.append('TCP')
                        elif ip[field]==17:
                            field_values.append('UDP')
                        elif ip[field]==1:
                            field_values.append('ICMP')
                        else:
                            field_values.append('None')
                    elif ip[field]:
                        if isinstance(ip[field],int):
                            field_values.append(ip[field])
                        else:
                            field_values.append(str(ip[field]))
                    else:
                        field_values.append(np.nan)
                except:
                    pass
            ## ICMP
            if hasattr(ip, 'icmp'):
                icmp = ip.icmp
                for field in icmp_fields:
                    try:
                        field = field.replace("ICMP_","")
                        if field != 'data': 
                            if field == 'code':
                                field_values.append(icmp.code)
                            elif icmp[field]:
                                if isinstance(icmp[field],int):
                                    field_values.append(icmp[field])
                                else:
                                    field_values.append(str(icmp[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                if hasattr(icmp.data, 'ip'):
                    ip = icmp.data.ip
            else:
                dataframe_filling = [np.nan] * (len(icmp_fields))
                field_values = field_values + dataframe_filling
            ## TCP
            if hasattr(ip, 'tcp'):
                transport = ip.tcp
                for field in tcp_fields:
                    try:
                        field = field.replace("TCP_","")
                        if field != 'data':
                            if field == 'opts':
                                field_values.append(len(transport[field]))
                            elif transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
            ## UDP
            elif hasattr(ip, 'udp'):
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                transport = ip.udp
                for field in udp_fields:
                    try:
                        field = field.replace("UDP_","")
                        if field != 'data': 
                            if transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
            ## OTHER PACKETS:
            else:
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
        ## Append transport layer payload
        if transport != None:           
            field_values.append(len(transport['data']))
            field_values.append(str(transport['data']))
            try:
                field_values.append(str(binascii.hexlify(transport['data'])))
            except:
                field_values.append(str(binascii.hexlify(transport['data'].data)))
        elif icmp != None:
            field_values.append(len(icmp['data']))
            field_values.append(str(icmp['data']))
            try:
                field_values.append(str(binascii.hexlify(icmp['data'])))
            except:
                field_values.append(str(repr(icmp['data'].data)))
        elif arp != None:           
            field_values.append(len(arp['data']))
            field_values.append(str(arp['data']))
            try:
                field_values.append(str(binascii.hexlify(arp['data'])))
            except:
                field_values.append(str(binascii.hexlify(arp['data'].data)))
        else:
            continue
        ## Add row to DF
        df_append = pd.DataFrame([field_values], columns=dataframe_fields)
        try:
            df = pd.concat([df, df_append], axis=0)
        except ValueError:
            raise
        n_packets = n_packets+1
    print('Finished iterating captured packets.')
    print('Total packets read: ',n_packets)
    ## Reset Index
    df = df.reset_index()
    ## Drop old index column
    df = df.drop(columns="index")
    return df

def pcap2dataframe_timestamp(pcap_file_path,selectionperiodduration,selectionperiodtype):  
    print('Starting reading .pcap file...')
    pcapReader = dpkt.pcap.Reader(open(pcap_file_path, "rb"))
    pcapReader = list(reversed(list(pcapReader))) #[:100]
    print('Finished reading .pcap file. \n')

    print('Converting .pcap into dataframe...')    
    ## Collect field names from Eth/IP/TCP/UDP (These will be columns in DF)

    ## ETH available fields:
        #eth_fields = ['data', 'dst', 'get_type', 'get_type_rev', 'ip', 'pack', 'pack_hdr', \
        #  'set_type', 'src', 'type', 'unpack']
    # ETH used fields:
    eth_fields = ['dst', 'src','ip', 'type'] 
    eth_fields = ['ETH_'+x for x in eth_fields]

    ## ARP available fields:
        #arp_fields = ['data', 'hln', 'hrd', 'op', 'pack', 'pack_hdr', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa', 'unpack']
    arp_fields = ['hln', 'hrd', 'op', 'pln', 'pro', 'sha', 'spa', 'tha', 'tpa']
    arp_fields = ['ARP_'+x for x in arp_fields]

    ## IP available fields:
        #ip_fields = ['data', 'df', 'dst', 'get_proto', 'hl', 'id', 'len', 'mf', \
        #    'off', 'offset', 'opts', 'p', 'pack', 'pack_hdr', 'rf', 'set_proto', 'src', \
        #        'sum', 'tcp', 'tos', 'ttl', 'unpack', 'v']
    # IP used fields:
    ip_fields = ['df', 'dst', 'hl', 'id', 'len', 'mf', \
        'off', 'offset', 'opts', 'p', 'rf', 'src', \
            'sum', 'tos', 'ttl', 'v']
    ip_fields = ['IP_'+x for x in ip_fields]
    
    ## TCP available fields:
        #tcp_fields = ['ack', 'data', 'dport', 'flags', 'off', 'opts', 'pack', \
        #     'pack_hdr', 'seq', 'sport', 'sum', 'unpack', 'urp', 'win']
    ## TCP used fields:
    tcp_fields = ['ack', 'dport', 'flags', 'off', 'opts', \
          'seq', 'sport', 'sum', 'urp', 'win']
    tcp_fields = ['TCP_'+x for x in tcp_fields]

    ## UDP available fields:
        #udp_fields = ['data', 'dport', 'pack', 'pack_hdr', 'sport', 'sum', 'ulen', 'unpack']
    ## UDP used fields:
    udp_fields = ['dport', 'sport', 'sum', 'ulen']
    udp_fields = ['UDP_'+x for x in udp_fields]

    ## ICMP available fields:
        #icmp_fields = ['code', 'data', 'echo', 'pack', 'pack_hdr', 'sum', 'type', 'unpack']
        #echo_fields = ['data', 'id', 'pack', 'pack_hdr', 'seq', 'unpack']
    icmp_fields = ['code', 'sum', 'type']
    icmp_fields = ['ICMP_'+x for x in icmp_fields]

    ## Payload fields:
    payload_fields = ['PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']

    ## Data in transport layer (TCP/UDP) is added afterwards
    dataframe_fields = ['timestamp'] + eth_fields + arp_fields + ip_fields + icmp_fields + tcp_fields + udp_fields + payload_fields
    
    # Create blank DataFrame
    df = pd.DataFrame(columns=dataframe_fields)
    
    n_packets = 0
    print('Starting iterating packets of the PCAP...')
    for ts, data in pcapReader:
        if n_packets==0:
            last_packet_ts=ts
            traininglimit = datetime.fromtimestamp(last_packet_ts)
            if selectionperiodtype=="Second":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - timedelta(seconds=selectionperiodduration)
            elif selectionperiodtype=="Minute":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - timedelta(minutes=selectionperiodduration)
            elif selectionperiodtype=="Hour":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - timedelta(hours=selectionperiodduration)
            elif selectionperiodtype=="Day":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - timedelta(days=selectionperiodduration)
            elif selectionperiodtype=="Week":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - timedelta(weeks=selectionperiodduration)
            elif selectionperiodtype=="Month":
                traininglimit = datetime.fromtimestamp(last_packet_ts) - relativedelta(months=+selectionperiodduration)
        if traininglimit > datetime.fromtimestamp(ts):
                break
        # Field array for each row of DataFrame
        ether = dpkt.ethernet.Ethernet(data)
        field_values = []
        field_values.append(ts)
        ## ETHERNET
        for field in eth_fields:
            try:
                field = field.replace("ETH_","")
                if field=='src' or field=='dst':
                    mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", ether[field]))
                    field_values.append(mac_address)
                elif ether[field]:
                    if isinstance(ether[field],int):
                        field_values.append(ether[field])
                    else:
                        field_values.append(str(ether[field]))
                else:
                    field_values.append(np.nan)
            except:
                pass
        ## ARP
        if hasattr(ether, 'arp'):
            arp = ether.arp
            for field in arp_fields:
                try:
                    field = field.replace("ARP_","")
                    if field != 'data':
                        if field=='sha' or field=='tha':
                            mac_address = str("%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", arp[field]))
                            field_values.append(mac_address)
                        elif field=='spa' or field=='tpa':
                            field_values.append(str(socket.inet_ntoa(arp[field])))
                        elif arp[field]:
                            if isinstance(arp[field],int):
                                field_values.append(arp[field])
                            else:
                                field_values.append(str(binascii.hexlify(arp[field])))
                        else:
                            field_values.append(np.nan)
                except:
                    field_values.append(np.nan)
            dataframe_filling = [np.nan] * (len(ip_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(tcp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(udp_fields))
            field_values = field_values + dataframe_filling
            dataframe_filling = [np.nan] * (len(icmp_fields))
            field_values = field_values + dataframe_filling
        ## IP
        if ether.type == dpkt.ethernet.ETH_TYPE_IP: 
            ip = ether.data
            dataframe_filling = [np.nan] * (len(arp_fields))
            field_values = field_values + dataframe_filling
            # Add all IP fields to dataframe
            for field in ip_fields:
                try:
                    field = field.replace("IP_","")
                    if field == 'opts':
                        field_values.append(len(ip[field]))
                    elif field=='src' or field=='dst':
                        field_values.append(str(socket.inet_ntoa(ip[field])))
                    
                    elif field=='p':
                        if ip[field]==6:
                            field_values.append('TCP')
                        elif ip[field]==17:
                            field_values.append('UDP')
                        elif ip[field]==1:
                            field_values.append('ICMP')
                        else:
                            field_values.append(ip[field])
                    elif ip[field]:
                        if isinstance(ip[field],int):
                            field_values.append(ip[field])
                        else:
                            field_values.append(str(ip[field]))
                    else:
                        field_values.append(np.nan)
                except:
                    pass
            ## ICMP
            if hasattr(ip, 'icmp'):
                icmp = ip.icmp
                for field in icmp_fields:
                    try:
                        field = field.replace("ICMP_","")
                        if field != 'data': 
                            if field == 'code':
                                field_values.append(icmp.code)
                            elif icmp[field]:
                                if isinstance(icmp[field],int):
                                    field_values.append(icmp[field])
                                else:
                                    field_values.append(str(icmp[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                if hasattr(icmp.data, 'ip'):
                    ip = icmp.data.ip
            else:
                dataframe_filling = [np.nan] * (len(icmp_fields))
                field_values = field_values + dataframe_filling
            ## TCP
            transport = None
            if hasattr(ip, 'tcp'):
                transport = ip.tcp
                for field in tcp_fields:
                    try:
                        field = field.replace("TCP_","")
                        if field != 'data':
                            if field == 'opts':
                                field_values.append(len(transport[field]))
                            elif transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
            ## UDP
            elif hasattr(ip, 'udp'):
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                transport = ip.udp
                for field in udp_fields:
                    try:
                        field = field.replace("UDP_","")
                        if field != 'data': 
                            if transport[field]:
                                if isinstance(transport[field],int):
                                    field_values.append(transport[field])
                                else:
                                    field_values.append(str(transport[field]))
                            else:
                                field_values.append(np.nan)
                    except:
                        field_values.append(np.nan)
            ## OTHER PACKETS:
            else:
                dataframe_filling = [np.nan] * (len(tcp_fields))
                field_values = field_values + dataframe_filling
                dataframe_filling = [np.nan] * (len(udp_fields))
                field_values = field_values + dataframe_filling
        ## Append transport layer payload
        if transport != None:           
            field_values.append(len(transport['data']))
            field_values.append(str(transport['data']))
            try:
                field_values.append(str(binascii.hexlify(transport['data'])))
            except:
                field_values.append(str(binascii.hexlify(transport['data'].data)))
        elif icmp != None:
            field_values.append(len(icmp['data']))
            field_values.append(str(icmp['data']))
            try:
                field_values.append(str(binascii.hexlify(icmp['data'])))
            except:
                field_values.append(str(repr(icmp['data'].data)))
        elif arp != None:           
            field_values.append(len(arp['data']))
            field_values.append(str(arp['data']))
            try:
                field_values.append(str(binascii.hexlify(arp['data'])))
            except:
                field_values.append(str(binascii.hexlify(arp['data'].data)))
        else:
            continue
        ## Add row to DF
        df_append = pd.DataFrame([field_values], columns=dataframe_fields)
        try:
            df = pd.concat([df, df_append], axis=0)
        except ValueError:
            raise
        n_packets = n_packets+1
    print('Finished iterating packets of the PCAP.')
    print('Total packets read: ',n_packets)
    ## Reset Index
    df = df.reset_index()
    ## Drop old index column
    df = df.drop(columns="index")
    return df