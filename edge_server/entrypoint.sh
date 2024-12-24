#!/bin/bash
set -e 
sleep 2
mkdir -p ${W1_MOUNT_POINT}/{28-00000677d509,28-0000067841b0}
echo -e "YES\nt=100" > ${W1_MOUNT_POINT}/28-00000677d509/w1_slave
echo -e "YES\nt=150" > ${W1_MOUNT_POINT}/28-0000067841b0/w1_slave

uvicorn chronos.app:app --host 0.0.0.0 --port 5171
