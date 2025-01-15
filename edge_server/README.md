# Chronos
## README

### What is this repository for?

Chronos is a boiling/cooling water system working on Raspberry Pi. Chronos has a web interface to control the system and tracking for the state.

Chronos talks to the following components on the RPI. These devices are specified in config.py and can be configured using  a .env file.
- Boiler via modbus connected to /dev/ttyUSB0
- Relays using emulated serial ports
- Water temperature in and out (1-wire protocol is used)

### API Endpoints

Once deployed, api endpoint documentation can be accessed at http://5173/api/docs


### Hardware dependencies

* Raspberry Pi
* USB to RS4485 adapter such as the GearMo Mini USB to RS485 / RS422 Converter FTDI CHIP
* Relay array such as the Numato 16 Channel USB Relay Module https://numato.com/product/16-channel-usb-relay-module
* Two DS18B20 temperature sensors connected to GPIO

# Deployment

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uvicorn chronos.app:app --host 0.0.0.0 --port 5171
```
