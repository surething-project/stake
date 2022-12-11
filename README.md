# STAKE
STAKE project code - Kevin B. Corrales - advisor Miguel L Pardal

## What is STAKE?
STAKE stands for: Secure Tracing of Anomalies using previous Knowledge and Extensions. \
The *tracing* component refers to the network traffic capture. \
The *previous knowledge* refers to rules that can be defined to recognise known attacks and enforce limits on device traffic. \
Finally, the *extensions* refer to the Machine Learning plug-ins that can be installed and used to detect unknown attacks.

STAKE can be installed on a Raspberry Pi 4 device and used to monitor and control a Smart Home network.  
The [demonstration](DEMO.md) illustrates how the tool operates.  
See the following instructions for installing and configuring STAKE.


## Hardware and Software versions used for Development

### Hardware
##### Raspberry Pi 4 Model B tech specs:
- Broadcom BCM2711, Quad core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz
- 2GB, 4GB or 8GB LPDDR4-3200 SDRAM (depending on model)
- 2.4 GHz and 5.0 GHz IEEE 802.11ac wireless, Bluetooth 5.0, BLE 
- Gigabit Ethernet
-  2 USB 3.0 ports; 2 USB 2.0 ports.
- Raspberry Pi standard 40 pin GPIO header (fully backwards compatible with previous boards)
- 2 micro-HDMI ports (up to 4kp60 supported)
- 2-lane MIPI DSI display port
- 2-lane MIPI CSI camera port
- 4-pole stereo audio and composite video port
- H.265 (4kp60 decode), H264 (1080p60 decode, 1080p30 encode)
- OpenGL ES 3.0 graphics
- Micro-SD card slot for loading operating system and data storage
- 5V DC via USB-C connector (minimum 3A*)
- 5V DC via GPIO header (minimum 3A*)
- Power over Ethernet (PoE) enabled (requires separate PoE HAT)
- Operating temperature: 0 – 50 degrees C ambient

### Software

##### Operating System:
- Operating System: Raspbian GNU/Linux 10 (buster)
- Linux Version: 4.19.97-v7l+ (dom@buildbot) (gcc version 4.9.3 (crosstool-NG crosstool-ng-1.22.0-88-g8460611)) 
- Home URL= http://www.raspbian.org/

##### Software versions:
- Python version: Python 3.7.3

## Installation and Configuration

1. Clone this repository.
2. Run installation script in the `installation` folder.
	```
	sh installation/install.sh
	```
	This script:
    - Installs the required Ubuntu and Python packages (list of the packages is located at `installation/packets-installed`).
    - Creates the PostgreSQL database and its tables.
3. Configure the network adapters. 
    The following configuration will set up the hardware as a Wireless Access Point:

	3.1 Install hostapd and dnsmasq:
	```
	sudo apt-get install hostapd
	sudo apt-get install dnsmasq
	```
	3.2 Turn off services so we can configure files safely:
	```
	sudo systemctl stop hostapd
	sudo systemctl stop dnsmasq
	```
	3.3 Configure a static IP for the wlan0 interface:
	```
	sudo nano /etc/dhcpcd.conf
	```
    - Add:
    
	    >  	interface wlan0 \
	    >	static ip_address=192.168.0.10/24 \
	    >	denyinterfaces eth0 \
    	>	denyinterfaces wlan0
	
	3.4 Configure the DHCP server (dnsmasq):
	```
	sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
	```
	```
	sudo nano /etc/dnsmasq.conf
	```
	- Add:

	    >    interface=wlan0 \
	    >    dhcp-range=192.168.0.11,192.168.0.50,255.255.255.0,24h
	
	3.5 Configure the access point host software (hostapd):
	```
    sudo nano /etc/hostapd/hostapd.conf 
	```
	- Add:
	
	    >	interface=wlan0 \
	    >	bridge=br0 \
	    >	hw_mode=g \
	    >	channel=7 \
	    >	wmm_enabled=0 \
	    >	macaddr_acl=0 \
	    >	auth_algs=1 \
	    >	ignore_broadcast_ssid=0 \
	    >	wpa=2 \
	    >	wpa_key_mgmt=WPA-PSK \
	    >	wpa_pairwise=TKIP \
	    >	rsn_pairwise=CCMP \
	    >	ssid=STAKE \
	    >	wpa_passphrase=kevinpi12345

	```
		sudo nano /etc/default/hostapd
	```
	
	- Add:
				
        >   DAEMON_CONF="/etc/hostapd/hostapd.conf"
	
    3.6 Set up traffic forwarding:

    ```
    sudo nano /etc/sysctl.conf
    ```

	- Uncomment (remove #):
	
	   > net.ipv4.ip_forward=1
	
	3.7 Add a new iptables rule:
	```
	sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
	sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
	sudo iptables-restore < /etc/iptables.ipv4.nat
	```
	3.8 Enable internet connection:
	```
	sudo apt-get install bridge-utils
	sudo brctl addbr br0
	sudo brctl addif br0 eth0
	```
	```
	sudo nano /etc/network/interfaces
	```
	- Add:
				
        >   auto br0 \
		>	iface br0 inet dhcp \
		>	bridge_ports eth0 wlan0

	3.9 Reboot:
	```
	sudo reboot
	```
	3.10 Turn on services if needed:
	```
	sudo systemctl start hostapd
	sudo systemctl start dnsmasq 
	```
4. Configure the STAKE system configuration file, located at `src/stake/config.ini`. 
    This configuration file allows us to configure: 
	- Web Server hosting settings
	- Database connection settings
	- STAKE system settings
	- Log settings

## Deployment
#### How to start and use the system?
1. Connect the desired devices to be used for anomaly detection to the STAKE system network.
    Default Wi-Fi settings:
    > SSID= STAKE \
    > Passphrase= kevinpi12345
2. Change directory to `src/stake`:
    ```
    cd src/stake
    ```
3. Start the system:
    ```
    sudo python3 run.py
    ```
4. Access the system interface via Web browser. 
    The default Web Server address to access the system is `<local IPv4 address>:5000`.
