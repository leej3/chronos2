#!/bin/bash -x

sp=`cat /home/rj/sp.txt`
/usr/local/bin/change_sp -s /dev/ttyUSB0 -t $sp
sleep 15
/usr/local/bin/change_sp -s /dev/ttyUSB0 -t $sp
sleep 15
/usr/local/bin/change_sp -s /dev/ttyUSB0 -t $sp
sleep 15
