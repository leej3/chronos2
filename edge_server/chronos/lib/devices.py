from serial import Serial
import sys
from datetime import datetime
from chronos.lib.config import cfg
from chronos.lib.logging import root_logger as logger
from pathlib import Path
import time
import asyncio
from pymodbus.client import ModbusSerialClient

def _ensure_event_loop():
    """Ensure there is an event loop available."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

class ModbusDevice:
    """
    A simple example class for a Modbus device using PyModbus 3.x
    """
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, parity='E'):
        # Ensure we have an event loop (needed for PyModbus internals)
        _ensure_event_loop()
        
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            timeout=1
        )
        connected = self.client.connect()
        if not connected:
            logger.warning(f"Unable to connect to Modbus device on {port}")

    def read_coil(self, address, unit=1):
        """
        Example method to read a coil. Returns True/False if successful, or None if error.
        """
        if not self.client:
            logger.error("Client not initialized or connection failed.")
            return None
        result = self.client.read_coils(address, 1, unit=unit)
        if result.isError():
            logger.error(f"Error reading coil {address}: {result}")
            return None
        return bool(result.bits[0]) if result.bits else None

    def set_coil(self, address, value, unit=1):
        """
        Example method to set a coil to True/False.
        """
        if not self.client:
            logger.error("Client not initialized or connection failed.")
            return None
        result = self.client.write_coil(address, value, unit=unit)
        if result.isError():
            logger.error(f"Error writing coil {address}: {result}")
            return None
        return True

    def close(self):
        """
        Closes the Modbus connection
        """
        if self.client:
            self.client.close()

class SerialDevice:
    def __init__(self, id: int, portname: str = "", baudrate: int = 19200):
        self.id = id
        self.portname = portname
        self.baudrate = baudrate
        self._state = None

    @property
    def state(self):
        """Return the last known state of the device. If _state is None, query the device."""
        return self._state if self._state is not None else self.read_state_from_device()

    @state.setter
    def state(self, desired_state: bool):
        """Set the device state by sending the appropriate command, then store it."""
        command_str = "on" if desired_state else "off"
        command = f"relay {command_str} {self.id}\n\r"
        response = self._send_command(command)
        self._state = desired_state

    def read_state_from_device(self) -> bool:
        """Query the device over serial to read its current state."""
        command = f"relay read {self.id}\n\r"
        response = self._send_command(command)

        # The response might look like:
        # 'relay read 0 \n\n\ron\n\r>'
        # or
        # 'relay read 1 \n\n\roff\n\r>'
        # We'll parse the response to determine on/off.
        lines = response.strip().split()
        if "on" in lines:
            self._state = True
        elif "off" in lines:
            self._state = False
        else:
            raise ValueError(f"Unable to parse device state from response: {response}")
        return self._state

    def _send_command(self, command: str) -> str:
        """Send a command to the device and return the raw response."""
        try:
            with Serial(self.portname, self.baudrate, timeout=1) as ser_port:
                ser_port.write(command.encode('utf-8'))
                response = ser_port.readall().decode('utf-8', errors='replace')
            return response
        except Exception as e:
            logger.warning(f"Serial port not accessible ([{e}]). Returning mock response for debugging.")
            parts = command.strip().split()
            device_id = parts[2] if len(parts) >= 3 else "0"
            return f"relay read {device_id} \n\n\roff\n\r>"

def c_to_f(t):
    return round(((9.0 / 5.0) * t + 32.0), 1)

def read_temperature_sensor(sensor_id):
    device_file = Path(cfg.sensors.mount_point, sensor_id, "w1_slave")
    while True:
        try:
            with open(device_file) as content:
                lines = content.readlines()
        except IOError as e:
            logger.error("Temp sensor error: {}".format(e))
            sys.exit(1)
        else:
            if lines[0].strip()[-3:] == "YES":
                break
            else:
                time.sleep(0.2)
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp = float(temp_string) / 1000.0
        return c_to_f(temp)


