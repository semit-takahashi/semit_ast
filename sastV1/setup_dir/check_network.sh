#!/bin/sh
/bin/ping -c 1 `netstat -r  | /bin/grep default | /usr/bin/awk '{print $2}'`
if [ $? -ne 0 ]; then
	echo "LINK IS DOWN ---- if reset"
	ip link set wlan0 down
	ip link set wlan0 up
else
	echo "LINK IS UP"
fi

# 
#sudo /etc/ifplugd/action.d/action_wpa wlan0 up
