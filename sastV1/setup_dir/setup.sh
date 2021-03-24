#!/bin/sh

LOG="SAST_monitor SAST_recorder STAT check_network SAST_machineSTAT"
DIR="/var/log/sast/"

# if exist LOG DIR , BACKUP
if [ -d ${DIR} ]; then
	echo "Exists ${DIR}  to BACKUP ${DIR}.back"
	mv ${DIR} ${DIR}../sast.back
fi

# make log directory
sudo mkdir -p  ${DIR}
sudo chmod 777 ${DIR}
sudo chown root:adm ${DIR}

# create logfile
for i in ${LOG} ; do
	touch ${DIR}${i}.log
	chown pi:pi ${DIR}${i}.log
	chmod ugo+r /${DIR}${i}.log
	if [ "$1" = "clear" ]; then 
		cp /dev/null ${DIR}${i}.log
	fi
done
echo "LOG DIR:${DIR}"
ls -ls ${DIR}
