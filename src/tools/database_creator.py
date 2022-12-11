from scapy.all import *
from os import stat
from os.path import exists

def create_database(path,adapter):
    if not exists(path):
            with open(path, 'w'): pass
    while stat(path).st_size<10737418240:
        packet = sniff(count=1,iface=adapter,prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))
        wrpcap(path, packet, append=True)
    print('\n\n IT REACHED 10 GB')

if __name__ == "__main__":
    create_database("/media/sf_VM-SharedFolder/Testing/my_home.pcap","eth0")
