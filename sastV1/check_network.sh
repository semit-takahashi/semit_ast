#!/bin/sh
# 2021/03/14 F.Takahashi
# for Raspberry Pi 
/bin/date '+%F %T'
/bin/ping -q -c 2 `netstat -r | /bin/grep default | /usr/bin/awk '{print $2}'`
if [ $? -ne 0 ]; then
	echo "LINK IS DOWN ---- if reset\n"
	ip link set wlan0 down
	ip link set wlan0 up
else
	echo "LINK IS UP\n"
fi
# 
#sudo /etc/ifplugd/action.d/action_wpa wlan0 up
