#!/bin/bash
#
#
#
#
#
# Script to run a command across multiple machines
# Global options
TIMEOUT=10
METRIC=K
MOBMETRICS_HOME=/opt/mobmetrics
CFG=$MOBMETRICS_HOME/config/devices_plan
MOBMETRICS_LOGS=$MOBMETRICS_HOME/logs
MOBMETRICS_BIN=$MOBMETRICS_HOME/bin
MOBMETRICS_SERVER=10.0.9.4

# Extract vars from config file
if [ -e $CFG ]
then
	gawk -F, '{ print $1" "$2" "$3" "$4" "$5}' $CFG | while read id meter plan down up; do
		ssh -n -oConnectTimeout=$TIMEOUT $meter "iperf -su -yC &"
		iperf -u -c $meter -b $down$METRIC -yC | tail -1 >> $MOBMETRICS_LOGS/$meter/$plan/download.txt
		ssh -n -oConnectTimeout=$TIMEOUT $meter "killall iperf"
		iperf -su -p$id -yC >> $MOBMETRICS_LOGS/$meter/$plan/upload.txt &
		ssh -n -oConnectTimeout=$TIMEOUT $meter "iperf -u -c $MOBMETRICS_SERVER -p $id -b $up$METRIC -yC"
		pid=`ps ax | grep "$id" | head -1 | gawk -F' ' '{ print $1 }'`
		kill -TERM $pid
		tail -1 $MOBMETRICS_LOGS/$meter/$plan/download.txt > /tmp/$meter-$plan-download-to-database.last
		tail -1 $MOBMETRICS_LOGS/$meter/$plan/upload.txt   > /tmp/$meter-$plan-upload-to-database.last
		python $MOBMETRICS_BIN/mobdm.py -down $id,$plan,/tmp/$meter-$plan-download-to-database.last
		python $MOBMETRICS_BIN/mobdm.py -up $id,$plan,/tmp/$meter-$plan-upload-to-database.last
	done
	sleep 5
	killall iperf
fi

