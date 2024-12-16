# Chronos #
## README ##

### What is this repository for? ###

Chronos is a boiling/cooling water system working on Raspberry Pi. Chronos has a web interface to control the system and tracking for the state.

![Alt text](http://i.imgur.com/8II1ydG.png "A screenshot of the Chronos web interface")
## Frontend and Backend Separation

### Overview

The Chronos project has been refactored to separate the frontend and backend components. The backend operates as a standalone service providing APIs, while the frontend is handled separately.

### A screenshot of API response of Chronos
![Alt text](https://miro.medium.com/v2/resize:fit:720/format:webp/1*p5MTHzrfaLYycSmZFSdmoA.png "A screenshot of API response of Chronos")

### API Endpoints

The backend provides the following API endpoints:

#### Base URL
- **Base URL**: `http://<backend-server-url>:90`

#### Endpoints

- **Get System Data**:
  - **URL**: `/`
  - **Method**: `GET`
  - **Description**: Retrieves the current system data, including temperature settings and mode status.
  - **Response**: JSON object containing system data.

- **Get Rendered Season Templates**:
  - **URL**: `/season_templates`
  - **Method**: `GET`
  - **Description**: Retrieves data for rendering season templates.
  - **Response**: JSON object with system results, activity stream, and efficiency details.

- **Download Log**:
  - **URL**: `/download_log`
  - **Method**: `GET`
  - **Description**: Downloads the system log as a CSV file.
  - **Response**: CSV file download.

- **Update Settings**:
  - **URL**: `/update_settings`
  - **Method**: `POST`
  - **Description**: Updates system settings based on provided form data.
  - **Request Body**: Form data with settings to update.
  - **Response**: JSON object with the updated form data.

- **Switch Mode**:
  - **URL**: `/switch_mode`
  - **Method**: `POST`
  - **Description**: Switches the system mode between winter and summer.
  - **Request Body**: Form data with the new mode (`TO_WINTER` or `TO_SUMMER`).
  - **Response**: JSON object with error status and mode switch lockout time.

- **Update Device State**:
  - **URL**: `/update_state`
  - **Method**: `POST`
  - **Description**: Updates the state of a specific device based on provided form data.
  - **Request Body**: Form data with device number and manual override value.
  - **Response**: Empty response.

- **Winter Mode Data**:
  - **URL**: `/winter`
  - **Method**: `GET`
  - **Description**: Retrieves data specific to the winter mode.
  - **Response**: JSON object with system data.

- **Summer Mode Data**:
  - **URL**: `/summer`
  - **Method**: `GET`
  - **Description**: Retrieves data specific to the summer mode.
  - **Response**: JSON object with system data.

- **Chart Data**:
  - **URL**: `/chart_data`
  - **Method**: `GET`
  - **Description**: Retrieves data for charts.
  - **Response**: JSON object containing chart data.
  

![Alt text](http://i.imgur.com/8II1ydG.png "A screenshot of the Chronos web interface")

### SIMULATORS

Chronos talks to the following components on the RPI. 

These devices are specified in data_files/chronos_config.json
- Boiler via modbus connected to /dev/ttyUSB0
- Chillers via relays talking to serial port /dev/ttyACM0
- Relays to the Chillers via /tmp/pty0 and /tmp/pty1
- Water temperature in and out via /tmp/water_in and /tmp/water_out

#### Test Chillers  
The relays to the chillers are emulated using socat. socat creates virtual pty devices that can respond as serial ports.
The following command in entrypoint.sh brings up a virtual ptyp1 device to respond to relays
```
socat -d -d PTY,link=/tmp/ptyp1,raw,echo=0 PTY,link=/tmp/ttyp1,raw,echo=0 &
```

#### Test Boiler  
The following commands in entrypoint.sh bring up a virtual ptyp0 device and then runs working-sync-server to emulate the boiler.
```
socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0 PTY,link=/tmp/ttyp0,raw,echo=0 &
python2 working-sync-server.py /tmp/ttyp0 &
```
Actual device to simulator mappings are as follows, the chronos_config.json needs to be changed on the automation QA server to run as follows:
Boiler --> /dev/ttyUSB0 --> /tmp/ptyp0
Chillers --> /dev/ttyACM0 --> /tmp/ptyp1

#### Test water temperature
The water temperature is provided in Centigrade. In order to provide a test incoming water temperature of 100C, use:
```
echo -e "YES\nt=100" > /tmp/water_in
```
In order to provide a test out water temperature of 140C, use:
```
echo -e "YES\nt=140" > /tmp/water_out
```

#### Python packages dependencies ####

* Flask
* pyserial
* apscheduler
* pymodbus
* sqlalchemy
* python-socketio
* socketIO_client
* uwsgi

#### System dependencies ####

* nginx
* uwsgi-plug-python

#### Hardware dependencies ####

* Raspberry Pi
* USB to RS4485 adapter such as the GearMo Mini USB to RS485 / RS422 Converter FTDI CHIP
* Relay array such as the Numato 16 Channel USB Relay Module https://numato.com/product/16-channel-usb-relay-module
* Two DS18B20 temperature sensors connected to GPIO 

#### Database configuration ####

TODO
#### Deployment instructions ####

To work with shared log and access to the db file www-data and pi users have to be added in one group.
Installation script does all required actions.

#### Files locations ####

chronos log directory: `/var/log/chronos`

chronos database directory: `/home/pi/chronos_db`

chronos config path: `/etc/chronos_config.json`

#### Managing ####
Chronos has a daemon which controlled by the following command:

`# service chronos start|stop|restart`

Web UI managed by uwsgi app server:

`# service uwsgi start|stop|restart|reload`

SocketIO server managing:

`# service uwsgi-socketio start|stop|restart|reload`

## AUTOMATION & TESTING

This repo uses a self-hosted git-runner on AWS. The .github/workflows/main.yaml file automatically kicks off a new deployment whenever any code changes have been committed to the master branch.

Follow these steps to add a new runner as shown in git
https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners

- Install docker.io and docker-compose on the Runner
  - sudo apt update
  - sudo apt install docker.io docker-compose -y
  



