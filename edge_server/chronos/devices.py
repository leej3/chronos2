import asyncio
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from chronos.config import cfg
from chronos.data_models import OperatingStatus
from chronos.logging import root_logger as logger
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from serial import Serial


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
def create_modbus_connection(port="/dev/ttyUSB0", baudrate=9600, parity="E", timeout=1):
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
        device = ModbusDevice(
            port=port, baudrate=baudrate, parity=parity, timeout=timeout
        )
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

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, parity="E", timeout=1):
        _ensure_event_loop()
        self.client = ModbusSerialClient(
            port=port, baudrate=baudrate, parity=parity, timeout=timeout
        )
        # Load register maps and mappings from config
        self.registers = cfg.modbus.registers
        self.operating_modes = cfg.modbus.operating_modes
        self.cascade_modes = cfg.modbus.cascade_modes
        self._connect()

    def _connect(self):
        if not self.client.connect():
            logger.warning("Unable to connect to Modbus device")

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

        Supported registers on this model:
        - Input registers (with +1 offset):
            - alarm, pump, flame status (30003-30005)
            - cascade power, water flow (30006-30007)
            - outlet, inlet, flue temps (30008-30010)
            - firing rate (30011)

        - Holding registers (no offset):
            - system supply temp (40006)

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
                i_result1 = self._read_input_register(
                    self.registers.input.alarm + 1, count=6
                )  # First chunk: alarm through water_flow
                i_result2 = self._read_input_register(
                    self.registers.input.outlet_temp + 1, count=4
                )  # Second chunk: temps and firing rate

                # Try reading supply temp holding register (known to work)
                try:
                    h_result1 = self._read_holding_register(
                        self.registers.holding.supply_temp, count=1
                    )
                    system_supply_temp = c_to_f(h_result1[0] / 10.0)
                except Exception as e:
                    logger.warning(f"Failed to read supply temp: {e}")
                    system_supply_temp = None

                boiler_stats = {
                    # Temperatures
                    "system_supply_temp": system_supply_temp,  # From holding register (available)
                    "outlet_temp": c_to_f(
                        i_result2[0] / 10.0
                    ),  # From input register (available)
                    "inlet_temp": c_to_f(
                        i_result2[1] / 10.0
                    ),  # From input register (available)
                    "flue_temp": c_to_f(
                        i_result2[2] / 10.0
                    ),  # From input register (available)
                    # Performance
                    "cascade_current_power": float(
                        i_result1[3]
                    ),  # From input register (available)
                    "lead_firing_rate": float(
                        i_result2[3]
                    ),  # From input register (available)
                    "water_flow_rate": float(
                        i_result1[4] / 10.0
                    ),  # From input register (available)
                    # Status
                    "pump_status": bool(
                        i_result1[1]
                    ),  # From input register (available)
                    "flame_status": bool(
                        i_result1[2]
                    ),  # From input register (available)
                }

                logger.info(f"Successfully read boiler data (attempt {attempt + 1})")
                logger.debug(f"Boiler stats: {boiler_stats}")
                return boiler_stats

            except (ModbusException, OSError, AttributeError, IndexError) as e:
                logger.error(
                    f"Failed to read boiler data (attempt {attempt + 1}): {str(e)}"
                )
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
        setpoint = int(
            ((float(effective_setpoint) - min_temp) / (max_temp - min_temp)) * 100
        )

        if not (0 <= setpoint <= 100):
            logger.error(
                f"Calculated setpoint {setpoint}% is out of valid range (0-100)"
            )
            return False

        for attempt in range(max_retries):
            try:
                # Write mode (4) to operating mode register
                result1 = self.client.write_register(
                    self.registers.holding.operating_mode, 4
                )
                if result1.isError():
                    raise ModbusException("Failed to write mode")

                # Write setpoint to setpoint register
                result2 = self.client.write_register(
                    self.registers.holding.setpoint, setpoint
                )
                if result2.isError():
                    raise ModbusException("Failed to write setpoint")

                logger.info(
                    f"Successfully set boiler setpoint to {effective_setpoint}°F ({setpoint}%) (attempt {attempt + 1})"
                )
                return True

            except (ModbusException, OSError) as e:
                logger.error(
                    f"Failed to set boiler setpoint (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(0.5)

        logger.error(f"Failed to set boiler setpoint after {max_retries} attempts")
        return False

    def close(self):
        """Close the Modbus connection and cleanup resources."""
        if self.client:
            self.client.close()

    def read_operating_status(self) -> OperatingStatus:
        """Read the current operating status of the boiler."""
        try:
            # Read operating mode and cascade mode
            operating_mode = self._read_holding_register(
                self.registers.holding.operating_mode
            )[0]
            cascade_mode = self._read_holding_register(
                self.registers.holding.cascade_mode
            )[0]

            # Read temperature values
            current_setpoint = self._read_holding_register(
                self.registers.holding.setpoint
            )[0]
            current_temp = self._read_holding_register(
                self.registers.input.outlet_temp + 1, count=1
            )[0]
            setpoint_temp = self._read_holding_register(
                self.registers.holding.setpoint, count=1
            )[0]

            # Read pressure from input register if available
            try:
                pressure = (
                    float(
                        self._read_input_register(
                            self.registers.input.pressure + 1, count=1
                        )[0]
                    )
                    / 10.0
                )  # Convert to PSI
            except Exception as e:
                logger.warning(f"Failed to read pressure: {e}")
                pressure = 0.0

            # Read error code if available
            try:
                error_code = self._read_holding_register(
                    self.registers.holding.error_code, count=1
                )[0]
            except Exception as e:
                logger.warning(f"Failed to read error code: {e}")
                error_code = 0

            # Get string representations
            operating_mode_str = self.operating_modes.get(operating_mode, "Unknown")
            cascade_mode_str = self.cascade_modes.get(cascade_mode, "Unknown")

            return OperatingStatus(
                operating_mode=operating_mode,
                operating_mode_str=operating_mode_str,
                cascade_mode=cascade_mode,
                cascade_mode_str=cascade_mode_str,
                current_setpoint=c_to_f(current_setpoint / 10.0),
                status=True,  # Boiler is responding, so status is True
                setpoint_temperature=c_to_f(setpoint_temp / 10.0),
                current_temperature=c_to_f(current_temp / 10.0),
                pressure=pressure,
                error_code=error_code,
            )
        except Exception as e:
            logger.error(f"Error reading operating status: {e}")
            return OperatingStatus(
                operating_mode=0,
                operating_mode_str="Error",
                cascade_mode=0,
                cascade_mode_str="Error",
                current_setpoint=0.0,
                status=False,  # Error occurred, so status is False
                setpoint_temperature=0.0,
                current_temperature=0.0,
                pressure=0.0,
                error_code=0,
            )


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
        self._send_command(command)
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
                ser_port.write(command.encode("utf-8"))
                response = ser_port.readall().decode("utf-8", errors="replace")
            return response
        except Exception as e:
            logger.warning(
                f"Serial port not accessible ([{e}]). Returning mock response for debugging."
            )
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
        temp_string = lines[1][equals_pos + 2 :]
        temp = float(temp_string) / 1000.0
        return c_to_f(temp)


def safe_read_temperature(sensor_id: str) -> Optional[float]:
    """Safely read temperature sensor with error handling."""
    try:
        return read_temperature_sensor(sensor_id)
    except Exception as e:
        logger.error(f"Error reading temperature sensor {sensor_id}: {e}")
        return None
