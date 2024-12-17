# HVAC Edge Server Deployment Guide

## System Requirements
- Raspberry Pi (3 or newer recommended)
- Python 3.8 or newer
- Network connectivity
- USB-to-Serial adapters for hardware communication

## Hardware Setup

### Serial Connections
1. Connect the USB-to-Serial adapter for HVAC control to `/dev/ttyUSB0`
2. Connect the USB-to-Serial adapter for Modbus to `/dev/ttyUSB1`

### GPIO Pins
- Temperature Sensor 1: GPIO17
- Temperature Sensor 2: GPIO18
- Chiller Control: GPIO23
- Boiler Control: GPIO24

## Software Installation

1. Update system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Install Python and required system packages:
```bash
sudo apt install -y python3-pip python3-venv
```

3. Create a project directory:
```bash
mkdir /opt/hvac-edge-server
cd /opt/hvac-edge-server
```

4. Clone the repository:
```bash
# Use your preferred method to transfer files to the Raspberry Pi
```

5. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

6. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit configuration:
```bash
nano .env
```

Important settings:
```
HOST=0.0.0.0
PORT=8000
DEBUG=False
ENVIRONMENT=production
MOCK_HARDWARE=False
MODBUS_PORT=/dev/ttyUSB0
SERIAL_PORT=/dev/ttyUSB1
```

## Running as a Service

1. Create systemd service file:
```bash
sudo nano /etc/systemd/system/hvac-edge-server.service
```

2. Add service configuration:
```ini
[Unit]
Description=HVAC Edge Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/hvac-edge-server
Environment=PATH=/opt/hvac-edge-server/venv/bin
ExecStart=/opt/hvac-edge-server/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:
```bash
sudo systemctl enable hvac-edge-server
sudo systemctl start hvac-edge-server
```

4. Check service status:
```bash
sudo systemctl status hvac-edge-server
```

## Monitoring

### View Logs
```bash
# View service logs
sudo journalctl -u hvac-edge-server

# View application logs
tail -f /opt/hvac-edge-server/hvac.log
```

### Check API Status
```bash
curl http://localhost:8000/api/state
```

## Troubleshooting

### Hardware Connection Issues
1. Check USB connections:
```bash
ls -l /dev/ttyUSB*
```

2. Verify permissions:
```bash
sudo usermod -a -G dialout pi
```

3. Test serial communication:
```bash
python3 -m serial.tools.miniterm /dev/ttyUSB0 9600
```

### Service Issues
1. Check service status:
```bash
sudo systemctl status hvac-edge-server
```

2. View detailed logs:
```bash
sudo journalctl -u hvac-edge-server -n 100 --no-pager
```

## Security Considerations

1. Network Access
   - Use firewall to restrict access to port 8000
   - Consider setting up reverse proxy with SSL
   - Implement authentication if exposed beyond local network

2. File Permissions
   - Ensure log files are only readable by service user
   - Protect .env file containing configuration

## Updating

1. Stop service:
```bash
sudo systemctl stop hvac-edge-server
```

2. Update code and dependencies:
```bash
cd /opt/hvac-edge-server
# Update code
pip install -r requirements.txt
```

3. Restart service:
```bash
sudo systemctl start hvac-edge-server
```