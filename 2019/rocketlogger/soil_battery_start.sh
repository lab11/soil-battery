#!/bin/bash

DATE_WITH_TIME=`date "+%Y%m%d-%H%M%S"`
NUMBER=`cat /home/rocketlogger/num.txt`
FNAME=soil_${DATE_WITH_TIME}_${NUMBER}.csv

echo $FNAME

rocketlogger stop
sleep 1s
rocketlogger cont -r 1 -f /home/rocketlogger/soil_battery/$FNAME -format csv -ch 0,1,2 -size 1g -d 0 -w 0
echo $(( $NUMBER+1 )) > /home/rocketlogger/num.txt

teroslogger -t /dev/ttyACM0