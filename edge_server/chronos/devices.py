from serial import Serial
import sys
from datetime import datetime
from chronos.config import cfg
from chronos.logging import root_logger as logger
from pathlib import Path
import time
import asyncio
from contextlib import contextmanager
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from typing import Optional

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

@contextmanager
def create_modbus_connection(port="/dev/ttyUSB0", baudrate=9600, parity='E', timeout=1):
    """
    Create a ModbusDevice connection using a context manager.

    Usage:
        with create_modbus_connection() as device:
            device.read_boiler_data()

    Args:
        port (str): Serial port path
        baudrate (int): Baud rate for serial communication
        parity (str): Parity setting ('N', 'E', 'O')
        timeout (int): Connection timeout in seconds

    Yields:
        ModbusDevice: A connected ModbusDevice instance

    Raises:
        ModbusException: If connection fails
    """
    device = None
    try:
        device = ModbusDevice(port=port, baudrate=baudrate, parity=parity, timeout=timeout)
        if not device.is_connected():
            raise ModbusException(f"Failed to connect to Modbus device on {port}")
        yield device
    finally:
        if device:
            device.close()

class ModbusDevice:
    """
    A Modbus device class that handles serial communication with proper resource management.
    Can be used either with context manager or directly:

    # Context manager usage (preferred):
    with create_modbus_connection() as device:
        device.read_boiler_data()

    # Direct usage:
    device = ModbusDevice()
    try:
        device.read_boiler_data()
    finally:
        device.close()
    """

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, parity='E', timeout=1):
        _ensure_event_loop()
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            timeout=timeout
        )
        # Load register maps and mappings from config
        self.registers = cfg.modbus.registers
        self.operating_modes = cfg.modbus.operating_modes
        self.cascade_modes = cfg.modbus.cascade_modes
        self.error_codes = cfg.modbus.error_codes
        self.model_ids = cfg.modbus.model_ids
        self._connect()

    def _connect(self):
        if not self.client.connect():
            logger.warning(f"Unable to connect to Modbus device")

    def is_connected(self):
        return self.client.is_socket_open()

    def _read_holding_register(self, address, count=1):
        """Read a holding register and handle errors."""
        result = self.client.read_holding_registers(address, count=count)
        if result.isError():
            raise ModbusException(f"Failed to read holding register {address}")
        return result.registers

    def _read_input_register(self, address, count=1):
        """Read an input register and handle errors."""
        result = self.client.read_input_registers(address, count=count)
        if result.isError():
            raise ModbusException(f"Failed to read input register {address}")
        return result.registers

    def read_boiler_data(self, max_retries=3):
        """
        Read various temperature and status data from the boiler.

        Available registers on this boiler model:
        - Input registers (with +1 offset):
            - alarm, pump, flame status (30003-30005)
            - cascade power, water flow (30006-30007)
            - outlet, inlet, flue temps (30008-30010)
            - firing rate (30011)

        - Holding registers (no offset):
            - system supply temp (40006)

        Unavailable registers on this model (attempted but not working):
            - DHW temp (40007)
            - min/max modulation rates (40014-40015)

        Args:
            max_retries (int): Maximum number of retry attempts

        Returns:
            dict: Dictionary containing boiler statistics, or None if read failed
        Raises:
            ModbusException: If device is not connected
        """
        if not self.is_connected():
            raise ModbusException("Device not connected")

        for attempt in range(max_retries):
            try:
                # Read input registers for status and performance (in chunks)
                # Note: Input registers are 30001-based, so we add 1 to the config values
                i_result1 = self._read_input_register(self.registers.input.alarm + 1, count=6)  # First chunk: alarm through water_flow
                i_result2 = self._read_input_register(self.registers.input.outlet_temp + 1, count=4)  # Second chunk: temps and firing rate

                # Try reading supply temp holding register (known to work)
                try:
                    h_result1 = self._read_holding_register(self.registers.holding.supply_temp, count=1)
                    system_supply_temp = c_to_f(h_result1[0] / 10.0)
                except Exception as e:
                    logger.warning(f"Failed to read supply temp: {e}")
                    system_supply_temp = None

                # The following registers were attempted but are not available on this model:
                """
                # DHW temp holding register
                h_result2 = self._read_holding_register(self.registers.holding.dhw_temp, count=1)
                dhw_temp = c_to_f(h_result2[0] / 10.0)

                # Min/max modulation rates
                h_result3 = self._read_holding_register(self.registers.holding.min_modulation, count=1)
                min_modulation = float(h_result3[0])
                h_result4 = self._read_holding_register(self.registers.holding.max_modulation, count=1)
                max_modulation = float(h_result4[0])
                """

                boiler_stats = {
                    # Temperatures
                    "system_supply_temp": system_supply_temp,  # From holding register (available)
                    "outlet_temp": c_to_f(i_result2[0] / 10.0),  # From input register (available)
                    "inlet_temp": c_to_f(i_result2[1] / 10.0),  # From input register (available)
                    "flue_temp": c_to_f(i_result2[2] / 10.0),  # From input register (available)
                    
                    # Performance
                    "cascade_current_power": float(i_result1[3]),  # From input register (available)
                    "lead_firing_rate": float(i_result2[3]),  # From input register (available)
                    "water_flow_rate": float(i_result1[4] / 10.0),  # From input register (available)
                    
                    # Status
                    "pump_status": bool(i_result1[1]),  # From input register (available)
                    "flame_status": bool(i_result1[2])  # From input register (available)
                    
                    # The following values were attempted but are not available:
                    # "dhw_temp": None,  # From holding register (not available)
                    # "min_modulation_rate": None,  # From holding register (not available)
                    # "max_modulation_rate": None  # From holding register (not available)
                }

                logger.info(f"Successfully read boiler data (attempt {attempt + 1})")
                logger.debug(f"Boiler stats: {boiler_stats}")
                return boiler_stats

            except (ModbusException, OSError, AttributeError, IndexError) as e:
                logger.error(f"Failed to read boiler data (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        logger.error(f"Failed to read boiler data after {max_retries} attempts")
        return None

    def set_boiler_setpoint(self, effective_setpoint, max_retries=3):
        """Set the boiler's temperature setpoint."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        # Convert Fahrenheit setpoint to a percentage (0-100)
        # Typical range: 120-180°F maps to 0-100%
        min_temp = 120.0
        max_temp = 180.0
        setpoint = int(((float(effective_setpoint) - min_temp) / (max_temp - min_temp)) * 100)

        if not (0 <= setpoint <= 100):
            logger.error(f"Calculated setpoint {setpoint}% is out of valid range (0-100)")
            return False

        for attempt in range(max_retries):
            try:
                # Write mode (4) to operating mode register
                result1 = self.client.write_register(self.registers.holding.operating_mode, 4)
                if result1.isError():
                    raise ModbusException("Failed to write mode")

                # Write setpoint to setpoint register
                result2 = self.client.write_register(self.registers.holding.setpoint, setpoint)
                if result2.isError():
                    raise ModbusException("Failed to write setpoint")

                logger.info(f"Successfully set boiler setpoint to {effective_setpoint}°F ({setpoint}%) (attempt {attempt + 1})")
                return True

            except (ModbusException, OSError) as e:
                logger.error(f"Failed to set boiler setpoint (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)

        logger.error(f"Failed to set boiler setpoint after {max_retries} attempts")
        return False

    def close(self):
        """Close the Modbus connection and cleanup resources."""
        if self.client:
            self.client.close()

    def read_operating_status(self):
        """Read operating mode, cascade mode, and current setpoint."""
        try:
            mode = self._read_holding_register(self.registers.holding.operating_mode)[0]
            cascade = self._read_holding_register(self.registers.holding.cascade_mode)[0]
            setpoint = self._read_holding_register(self.registers.holding.setpoint)[0]

            return {
                "operating_mode": mode,
                "operating_mode_str": self.operating_modes.get(str(mode), f"Unknown ({mode})"),
                "cascade_mode": cascade,
                "cascade_mode_str": self.cascade_modes.get(str(cascade), f"Unknown ({cascade})"),
                "current_setpoint": c_to_f(setpoint / 10.0)
            }
        except ModbusException as e:
            logger.error(f"Failed to read operating status: {e}")
            return {}

    def read_error_history(self):
        """Read error history including last lockout and blockout codes."""
        try:
            # Read last lockout and blockout codes
            error_regs = self._read_holding_register(self.registers.holding.last_lockout, count=2)
            
            error_history = {}
            
            # Process lockout code
            lockout_code = error_regs[0]
            if 0 <= lockout_code < len(self.error_codes):
                error_history.update({
                    "last_lockout_code": lockout_code,
                    "last_lockout_str": self.error_codes.get(str(lockout_code), f"Unknown ({lockout_code})")
                })
            else:
                logger.warning(f"Invalid lockout code: {lockout_code}")
            
            # Process blockout code
            blockout_code = error_regs[1]
            if 0 <= blockout_code < len(self.error_codes):
                error_history.update({
                    "last_blockout_code": blockout_code,
                    "last_blockout_str": self.error_codes.get(str(blockout_code), f"Unknown ({blockout_code})")
                })
            else:
                logger.warning(f"Invalid blockout code: {blockout_code}")
            
            return error_history
        except ModbusException as e:
            logger.debug(f"Error history not available: {e}")
            return {}

    def read_model_info(self):
        """Read boiler model information and firmware versions."""
        try:
            # Read model ID and version information
            info_regs = self._read_holding_register(self.registers.holding.model_id, count=3)
            
            model_info = {}
            
            # Process model ID
            model_id = info_regs[0]
            model_info["model_id"] = model_id
            model_info["model_name"] = self.model_ids.get(str(model_id), f"Unknown Model ({model_id})")
            
            # Process firmware version
            fw_ver = info_regs[1]
            major = (fw_ver >> 8) & 0xFF
            minor = fw_ver & 0xFF
            model_info["firmware_version"] = f"{major}.{minor}"
            
            # Process hardware version
            hw_ver = info_regs[2]
            major = (hw_ver >> 8) & 0xFF
            minor = hw_ver & 0xFF
            model_info["hardware_version"] = f"{major}.{minor}"
            
            return model_info
        except ModbusException as e:
            logger.debug(f"Model information not available: {e}")
            return {}

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
            raise e
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


def safe_read_temperature(sensor_id: str) -> Optional[float]:
    """Safely read temperature sensor with error handling."""
    try:
        return read_temperature_sensor(sensor_id)
    except Exception as e:
        logger.error(f"Error reading temperature sensor {sensor_id}: {e}")
        return None
