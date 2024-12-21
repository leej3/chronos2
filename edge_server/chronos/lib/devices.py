from serial import Serial
import sys
from datetime import datetime
from chronos.lib.config import cfg
from chronos.lib.logging import root_logger as logger
from pathlib import Path
import time
import asyncio
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit."""
    return round(((9.0 / 5.0) * celsius + 32.0), 1)

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
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, parity='E', unit=1):
        # Ensure we have an event loop (needed for PyModbus internals)
        _ensure_event_loop()
        self.unit = unit
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

    def set_boiler_setpoint(self, effective_setpoint, max_retries=3):
        """
        Set the boiler's temperature setpoint.
        
        Args:
            effective_setpoint (float): The desired temperature setpoint
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert the setpoint using the provided formula
        setpoint = int(-101.4856 + 1.7363171 * float(effective_setpoint))
        
        if not (0 < setpoint < 100):
            logger.error(f"Calculated setpoint {setpoint} is out of valid range (0-100)")
            return False
            
        for attempt in range(max_retries):
            try:
                # Write mode (4) to register 0
                result1 = self.client.write_register(0, 4, unit=self.unit)
                if result1.isError():
                    raise ModbusException("Failed to write mode")
                    
                # Write setpoint to register 2
                result2 = self.client.write_register(2, setpoint, unit=self.unit)
                if result2.isError():
                    raise ModbusException("Failed to write setpoint")
                    
                logger.info(f"Successfully set boiler setpoint to {setpoint} (attempt {attempt + 1})")
                return True
                
            except (ModbusException, OSError) as e:
                logger.error(f"Failed to set boiler setpoint (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    
        logger.error(f"Failed to set boiler setpoint after {max_retries} attempts")
        return False

    def read_boiler_data(self, max_retries=3):
        """
        Read various temperature and status data from the boiler.
        
        Args:
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            dict: Dictionary containing boiler statistics, or None if read failed
        """
        for attempt in range(max_retries):
            try:
                # Read system supply temperature (holding register 40006)
                h_result = self.client.read_holding_registers(6, count=1, unit=self.unit)
                if h_result.isError():
                    raise ModbusException("Failed to read holding registers")

                # Read input registers (30003-30011)
                i_result = self.client.read_input_registers(3, count=9, unit=self.unit)
                if i_result.isError():
                    raise ModbusException("Failed to read input registers")

                boiler_stats = {
                    "system_supply_temp": c_to_f(h_result.registers[0] / 10.0),
                    "outlet_temp": c_to_f(i_result.registers[5] / 10.0),
                    "inlet_temp": c_to_f(i_result.registers[6] / 10.0),
                    "flue_temp": c_to_f(i_result.registers[7] / 10.0),
                    "cascade_current_power": float(i_result.registers[3]),
                    "lead_firing_rate": float(i_result.registers[8])
                }
                
                logger.info(f"Successfully read boiler data (attempt {attempt + 1}): {boiler_stats}")
                return boiler_stats

            except (ModbusException, OSError, AttributeError, IndexError) as e:
                logger.error(f"Failed to read boiler data (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        logger.error(f"Failed to read boiler data after {max_retries} attempts")
        return None

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


