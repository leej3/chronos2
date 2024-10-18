#!/bin/bash
set -e 

socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0 PTY,link=/tmp/ttyp0,raw,echo=0 &
socat -d -d PTY,link=/tmp/ptyp1,raw,echo=0 PTY,link=/tmp/ttyp1,raw,echo=0 &
python2 -u working-sync-server.py /tmp/ttyp0 &

sudo chown pi:pi /tmp/ptyp0
sudo chown pi:pi /tmp/ptyp1
sudo chown -R pi:pi /home/pi

sleep 2
mkdir -p /var/log/uwsgi

/usr/local/bin/uwsgi --version

/usr/local/bin/uwsgi --ini /etc/uwsgi/apps-enabled/socketio_server.ini --pidfile /var/run/uwsgi/uwsgi-socketio.pid --daemonize /var/log/uwsgi/uwsgi-socketio.log

echo -e "YES\nt=100" > /tmp/water_in
echo -e "YES\nt=150" > /tmp/water_out

service uwsgi start
service nginx start
service chronos start
service chronos restart



tail -f /dev/null
