FROM --platform=linux/arm raspbian/systemd:latest
workdir /home/chronos

RUN echo "deb http://legacy.raspbian.org/raspbian stretch main contrib non-free rpi" > /etc/apt/sources.list


run apt-get install socat -y



copy . .
copy chronos.sql /home/pi/chronos_db/
run chmod +x entrypoint.sh

entrypoint [ "./entrypoint.sh" ]

