#! /bin/bash
# Read Temperature

while true;do
tempread1=`cat /sys/bus/w1/devices/28-000006764525/w1_slave`
tempread2=`cat /sys/bus/w1/devices/28-00000677d509/w1_slave`

# Format
temp1=`echo "scale=2; "\`echo ${tempread1##*=}\`" / 1000 * 9 /5 +32" | bc`
temp2=`echo "scale=2; "\`echo ${tempread2##*=}\`" / 1000 * 9 /5 +32" | bc`

# Output
echo -n "Inlet " $temp2 "°F - Outlet " $temp1 "°F "
date +%T
sleep 5
done
