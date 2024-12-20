from serial import Serial
import sys
from datetime import datetime
from chronos.lib.config import cfg
from chronos.lib.logging import root_logger as logger
from pathlib import Path
import time

class Device:
    def __init__(self, id: int, portname: str = "/dev/ttyACM0", baudrate: int = 19200):
        self.id = id
        self.portname = portname
        self.baudrate = baudrate
        self._state = None  # Now we store the actual state in this private attribute

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
        # Clean and split the response.
        lines = response.strip().split()
        # Look for "on" or "off" in the response
        if "on" in lines:
            self._state = True
        elif "off" in lines:
            self._state = False
        else:
            # If we cannot determine state, you might raise an exception or handle it gracefully
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

            # Extract device ID from the command
            parts = command.strip().split()
            device_id = parts[2] if len(parts) >= 3 else "0"

            # Return a mock "read" response that includes the correct device ID
            return f"relay read {device_id} \n\n\roff\n\r>"

def c_to_f(t):
    return round(((9.0 / 5.0) * t + 32.0), 1)

def read_temperature_sensor(sensor_id):
        #return 50
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
            # Divide by 1000 for proper decimal point
            temp = float(temp_string) / 1000.0
            # Convert to degF
            return c_to_f(temp)


