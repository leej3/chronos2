FROM --platform=linux/arm raspbian/systemd:latest
workdir /home/chronos

RUN echo "deb http://legacy.raspbian.org/raspbian stretch main contrib non-free rpi" > /etc/apt/sources.list
run apt-get update -y && apt-get install python2.7 python-pip cron sqlite3 nginx libssl-dev vim -y
run useradd pi
run mkdir -p /home/pi/chronos_db
run CFLAGS="-I/usr/include/openssl" && LDFLAGS="-L/usr/lib/arm-linux-gnueabihf" && UWSGI_PROFILE_OVERRIDE=ssl=true && pip install -trusted-host pypi.org --trusted-host files.pythonhosted.or -I --no-binary=:all: --no-cache-dir uwsgi==2.0.20
RUN pip install flask==1.1.4 flask-cors==3.0.10 pyserial pymodbus APScheduler==3.6.3
run pip install --upgrade setuptools
run pip install sqlalchemy python-socketio==0.4.1 socketIO_client six==1.15.0
run pip install gevent
run pip install python-engineio==3.11.2 python-socketio==4.4.0
run pip install gevent-websocket


run apt-get install python3 python3-pip socat -y



copy . .
copy chronos.sql /home/pi/chronos_db/
run python setup.py install
run rm /etc/nginx/sites-enabled/default
run ln -s /etc/nginx/sites-enabled/chronos_conf /etc/nginx/sites-enabled/default
RUN pip install uwsgi
run /usr/local/bin/uwsgi --ini /etc/uwsgi/apps-enabled/socketio_server.ini --pidfile /var/run/uwsgi/uwsgi-socketio.pid --daemonize /var/log/uwsgi/uwsgi-socketio.log
run chmod +x entrypoint.sh

entrypoint [ "./entrypoint.sh" ]

