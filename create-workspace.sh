#!/bin/bash
#
#
#
# Script to run a command across multiple machines
# Global options
MOBMETRICS_HOME=/opt/mobmetrics
CFG=$MOBMETRICS_HOME/config/devices_plan
MOBMETRICS_LOGS=$MOBMETRICS_HOME/logs
MOBMETRICS_BIN=$MOBMETRICS_HOME/bin
# Extract vars from config file
if [ -e $CFG ]
then
	gawk -F, '{ print $2" "$3}' $CFG | while read meter plan; do
	if [ -d $MOBMETRICS_LOGS/$meter ]
	then
		echo "Directory $meter Exists!"
		if [ -d $MOBMETRICS_LOGS/$meter/$plan ]
		then
			echo "SubDirectory $meter/$plan Exists!"
		else
			mkdir $MOBMETRICS_LOGS/$meter/$plan
		fi
			
	else
		mkdir $MOBMETRICS_LOGS/$meter
		mkdir $MOBMETRICS_LOGS/$meter/$plan
	fi
	done
fi

