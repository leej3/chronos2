#!/bin/bash
set -e 

socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0 PTY,link=/tmp/ttyp0,raw,echo=0 &
socat -d -d PTY,link=/tmp/ptyp1,raw,echo=0 PTY,link=/tmp/ttyp1,raw,echo=0 &
# python working-sync-server.py /tmp/ttyp0 &

sleep 2
echo -e "YES\nt=100" > /tmp/water_in
echo -e "YES\nt=150" > /tmp/water_out


fastapi run --host 0.0.0.0 --port 5171 --reload