import subprocess,psutil

#CPU
def get_cpu_usage():
    cpu_usage = str(psutil.cpu_percent(interval=1)) +"%"
    return cpu_usage

def get_cpu_temp():
    if not hasattr(psutil, "sensors_temperatures"):
        print("platform not supported")
    temps = psutil.sensors_temperatures()
    if not temps:
        print("can't read any temperature")
    for name, entries in temps.items():
        print(name)
        for entry in entries:
            print("    %-20s %s °C (high = %s °C, critical = %s °C)" % (
                entry.label or name, entry.current, entry.high,
                entry.critical))

#Virtual Memory (RAM)
def get_mem_total():
    ram = psutil.virtual_memory() 
    ram_total = str( round((ram.total / 2**30),2) )  +" GB"     # GiB.
    return ram_total

def get_mem_used():
    ram = psutil.virtual_memory() 
    ram_used = str( round(( (ram.total - ram.available) / 2**30),2) )  +" GB"     # GiB.
    return ram_used

def get_mem_usage():
    ram = psutil.virtual_memory() 
    ram_usage = str(ram.percent) +"%"
    return ram_usage

#Swap Memory
def get_swap_total():
    swap = psutil.swap_memory() 
    swap_total = str( round((swap.total / 2**30),2) )  +" GB"     # GiB.
    return swap_total

def get_swap_used():
    swap = psutil.swap_memory() 
    swap_used = str( round(( swap.used / 2**30),2) )  +" GB"     # GiB.
    return swap_used

def get_swap_usage():
    swap = psutil.swap_memory() 
    swap_usage = str(swap.percent) +"%"
    return swap_usage

#Disk
def get_disk_total():
    disk = psutil.disk_usage('/')
    disk_total = str( round((disk.total / 2**30),2) )  +" GB"     # GiB.
    return disk_total

def get_disk_used():
    disk = psutil.disk_usage('/')
    disk_used = str( round(( disk.used / 2**30),2) )  +" GB"     # GiB.
    return disk_used

def get_disk_usage():
    disk = psutil.disk_usage('/')
    disk_usage = str(disk.percent) +"%"
    return disk_usage

#Network
def get_bytes_sent():
    net = psutil.net_io_counters(pernic=True)
    sum_bytes = 0
    for interface in net:
        sum_bytes +=   net[interface].bytes_sent / 2**20 
    sent = str( round(sum_bytes,2) ) +" Mb/s"
    return sent

def get_bytes_recv():
    net = psutil.net_io_counters(pernic=True)
    sum_bytes = 0
    for interface in net:
        sum_bytes +=   net[interface].bytes_recv / 2**20 
    received = str( round(sum_bytes,2) ) +" Mb/s"
    return received

def get_bytes_percentage():
    net = psutil.net_io_counters(pernic=True)
    sum_recv_bytes = 0
    sum_sent_bytes= 0
    for interface in net:
        sum_recv_bytes +=   net[interface].bytes_recv / 2**20 
        sum_sent_bytes +=   net[interface].bytes_sent / 2**20

    sum_total = sum_sent_bytes+sum_recv_bytes
    percentage = str((sum_recv_bytes/ sum_total)*100)+"%"
    return percentage

def get_interfaces(stake_interface):
    net = psutil.net_io_counters(pernic=True)
    interfaces = ""
    net_len = len(net)-1
    counter = 0
    for interface in net:
        if interface == stake_interface:
            interfaces += interface
            if counter != net_len:
                interfaces += "/"
            counter+=1
    return interfaces

# def get_interfaces_list(stake_interface):
#     interfaces = psutil.net_if_addrs()
#     adapters = [("None","None")]
#     for interface in interfaces:
#         if interface == stake_interface:
#             adapters.append( (interface,interface))
#     return adapters

def get_interfaces_progress(stake_interface):
    net = psutil.net_io_counters(pernic=True)
    html=""
    for interface in net:
        if interface == stake_interface:
            percentage = round(((net[interface].bytes_recv / (net[interface].bytes_recv+net[interface].bytes_sent))*100),2)
            percentage = str(percentage)+"%"
            recv_bytes =   str(round(net[interface].bytes_recv / 2**20,2))+" Mb/s"
            sent_bytes =   str(round(net[interface].bytes_sent / 2**20,2))+" Mb/s"
            html+= "<div class=\"key pull-right\">"+interface+"</div> <div class=\"stat\"> \
                <div class=\"info\">"+ recv_bytes+ "<i class=\"fa fa-caret-down\"></i> &nbsp;"+ \
                sent_bytes+"<i class=\"fa fa-caret-up\"></i></div><div class=\"progress progress-small\"> \
                <div class=\"progress-bar progress-bar-inverse\" style=\"width:"+ percentage+";\"></div></div></div>"
    return html

#SYSTEM
def get_os_info():
    os_info = subprocess.run(['cat', '/etc/os-release'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    os_version = subprocess.run(['cat', '/proc/version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    os_version = "<p>"+os_version.replace("\n","</p><p>")+"</p>"
    os_info = "<p>"+os_info.replace("\n","</p><p>")+"</p>"+ os_version 
    return os_info

def get_cpu_info():
    cpu_info = subprocess.run(['cat', '/proc/cpuinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    cpu_info = "<p>"+cpu_info.replace("\n","</p><p>")+"</p>"
    return cpu_info

def get_mem_info():
    mem_info = subprocess.run(['cat', '/proc/meminfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    mem_info = "<p>"+mem_info.replace("\n","</p><p>")+"</p>"
    return mem_info

def get_network_info(stake_interface):
    network_info = subprocess.run(['ifconfig', stake_interface], stdout=subprocess.PIPE).stdout.decode('utf-8')
    network_info = network_info.replace("\n\n","<hr><br>")
    network_info = "<p>"+network_info.replace("\n","</p><p>")+"</p>"
    return network_info