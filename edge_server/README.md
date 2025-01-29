# Chronos
## README

### What is this repository for?

Chronos is a boiling/cooling water system working on Raspberry Pi. Chronos has a web interface to control the system and tracking for the state.

Chronos talks to the following components on the RPI. These devices are specified in config.py and can be configured using  a .env file.
- Boiler via modbus connected to /dev/ttyUSB0
- Relays using emulated serial ports
- Water temperature in and out (1-wire protocol is used)

### API Endpoints

Once deployed, api endpoint documentation can be accessed at http://5171/api/docs


### Hardware dependencies

* Raspberry Pi
* USB to RS4485 adapter such as the GearMo Mini USB to RS485 / RS422 Converter FTDI CHIP
* Relay array such as the Numato 16 Channel USB Relay Module https://numato.com/product/16-channel-usb-relay-module
* Two DS18B20 temperature sensors connected to GPIO

# Deployment

You can either run the service directly:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run uvicorn chronos.app:app --host 0.0.0.0 --port 5171
```

Or install it as a systemd service (recommended for production):
```bash
sudo ./install.sh
```

The installation script will:
- Create the installation directory at `/opt/chronos`
- Install the uv package manager if not present
- Install all dependencies
- Configure and start the systemd service

You can manage the service using standard systemd commands:
```bash
# View service status
sudo systemctl status chronos

# View logs
sudo journalctl -u chronos -f

# Stop the service
sudo systemctl stop chronos

# Start the service
sudo systemctl start chronos

# Restart the service
sudo systemctl restart chronos
```
