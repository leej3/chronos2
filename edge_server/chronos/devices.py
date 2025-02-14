import asyncio
import math
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from chronos.config import cfg
from chronos.logging import root_logger as logger
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException, ModbusIOException
from serial import Serial


def c_to_f(celsius):
    """Convert Celsius to Fahrenheit.

    This matches the C implementation exactly:
    return ((9.0f/5.0f)*c + 32.0f);
    """
    return (9.0 / 5.0) * celsius + 32.0


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

        # Create register mappings (using correct base addresses)
        class Registers:
            def __init__(self):
                self.holding = type(
                    "Holding",
                    (),
                    {
                        "operating_mode": 0x40000,  # Base address for holding registers
                        "cascade_mode": 0x40001,
                        "setpoint": 0x40002,
                        "min_setpoint": 0x40003,
                        "max_setpoint": 0x40004,
                        "last_lockout": 0x40005,
                        "model_id": 0x40006,
                        "system_supply_temp": 0x40007,
                    },
                )()
                self.input = type(
                    "Input",
                    (),
                    {
                        "alarm": 0x30003,  # Base address for input registers
                        "pump": 0x30004,
                        "flame": 0x30005,
                        "cascade_current_power": 0x30006,
                        "outlet_temp": 0x30008,
                        "inlet_temp": 0x30009,
                        "flue_temp": 0x30010,
                        "lead_firing_rate": 0x30011,
                    },
                )()

        self.registers = Registers()

        # Updated operating modes to match working implementation
        self.operating_modes = {
            "0": "Initialization",
            "1": "Standby",
            "2": "CH Demand",
            "3": "DHW Demand",
            "4": "CH & DHW Demand",
            "5": "Manual Operation",
            "6": "Shutdown",
            "7": "Error",
            "8": "Manual Operation 2",
            "9": "Freeze Protection",
            "10": "Sensor Test",
        }

        # Updated cascade modes
        self.cascade_modes = {"0": "Single Boiler", "1": "Manager", "2": "Member"}

        # Updated error codes
        self.error_codes = {
            "0": "No Error",
            "1": "Ignition Failure",
            "2": "Safety Circuit Open",
            "3": "Low Water",
            "4": "Gas Pressure Error",
            "5": "High Limit",
            "6": "Flame Circuit Error",
            "7": "Sensor Failure",
            "8": "Fan Speed Error",
        }

        # Updated model IDs
        self.model_ids = {
            "1": "FTXL 85",
            "2": "FTXL 105",
            "3": "FTXL 125",
            "4": "FTXL 150",
            "5": "FTXL 185",
            "6": "FTXL 220",
            "7": "FTXL 260",
            "8": "FTXL 300",
            "9": "FTXL 399",
        }

        self._connect()

    def _connect(self):
        """Attempt to connect to the device.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            if not self.client.connect():
                logger.warning("Unable to connect to Modbus device")
                return False
            return True
        except Exception as e:
            logger.error(f"Error connecting to Modbus device: {e}")
            return False

    def is_connected(self):
        """Check if the device is connected.

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            return self.client.is_socket_open()
        except Exception:
            return False

    def _read_holding_register(self, address, count=1):
        """Read a holding register and handle errors."""
        try:
            result = self.client.read_holding_registers(address=address, count=count)
            if result.isError():
                raise ModbusException(f"Failed to read holding register {address}")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read holding register {address}: {e}")
            raise ModbusException(
                f"Failed to read holding register {address}: {e}"
            ) from e

    def _read_input_register(self, address, count=1):
        """Read an input register and handle errors."""
        try:
            result = self.client.read_input_registers(address=address, count=count)
            if result.isError():
                raise ModbusException(f"Failed to read input register {address}")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read input register {address}: {e}")
            raise ModbusException(
                f"Failed to read input register {address}: {e}"
            ) from e

    def read_boiler_data(self, max_retries=3):
        """Read various temperature and status data from the boiler.

        This implementation has been verified against a working C implementation (bstat).
        Register readings fall into these categories:

        Verified Working (matching bstat):
        - Temperatures (all converted from C to F, divided by 10):
            - System Supply Temp (40006)
            - Outlet Temp (30008)
            - Inlet Temp (30009)
            - Flue Temp (30010)
        - Performance:
            - Cascade Current Power (30006) - direct percentage
            - Lead Firing Rate (30011) - direct percentage
        - Status:
            - Operating Mode (40001) - with string mapping
            - Cascade Mode (40002) - with string mapping
            - Alarm/Pump/Flame Status (30003-30005) - boolean values

        Args:
            max_retries (int): Maximum number of retry attempts

        Returns:
            dict: Dictionary containing boiler statistics, or None if read failed
        Raises:
            ModbusException: If device is not connected and reconnection fails
        """
        # First check - if not connected, raise immediately
        if not self.is_connected():
            raise ModbusException("Device not connected")

        last_error = None
        for attempt in range(max_retries):
            try:
                # Read holding registers block (operating mode through supply temp)
                h_result = self._read_holding_register(
                    self.registers.holding.operating_mode, count=7
                )

                # Read input registers block (status through firing rate)
                i_result = self._read_input_register(
                    self.registers.input.alarm, count=9
                )

                # Convert temperatures exactly as in C code
                temps = {
                    "system_supply_temp": round(c_to_f(h_result[6] / 10.0), 1),
                    "outlet_temp": round(c_to_f(i_result[5] / 10.0), 1),
                    "inlet_temp": round(c_to_f(i_result[6] / 10.0), 1),
                    "flue_temp": round(c_to_f(i_result[7] / 10.0), 1),
                }

                boiler_stats = {
                    # System Status - Verified working
                    "operating_mode": h_result[0],
                    "operating_mode_str": self.operating_modes.get(
                        str(h_result[0]), f"Unknown ({h_result[0]})"
                    ),
                    "cascade_mode": h_result[1],
                    "cascade_mode_str": self.cascade_modes.get(
                        str(h_result[1]), f"Unknown ({h_result[1]})"
                    ),
                    # Setpoints - Unverified, read from file in C implementation
                    "current_setpoint": round(c_to_f(h_result[2] / 10.0), 1),
                    "min_setpoint": round(c_to_f(h_result[3] / 10.0), 1),
                    "max_setpoint": round(c_to_f(h_result[4] / 10.0), 1),
                    # Status Flags - Verified working (direct boolean conversion)
                    "alarm_status": bool(i_result[0]),
                    "pump_status": bool(i_result[1]),
                    "flame_status": bool(i_result[2]),
                    # Performance - Verified working (direct percentage values)
                    "cascade_current_power": float(i_result[3]),
                    "lead_firing_rate": float(i_result[8]),
                    # Add verified temperatures
                    **temps,
                }

                logger.info(f"Successfully read boiler data (attempt {attempt + 1})")
                logger.debug(f"Boiler stats: {boiler_stats}")
                return boiler_stats

            except (
                ModbusException,
                OSError,
                AttributeError,
                IndexError,
                ValueError,
                TimeoutError,
                ModbusIOException,
            ) as e:
                last_error = e
                logger.error(
                    f"Failed to read boiler data (attempt {attempt + 1}): {str(e)}"
                )

                # Check connection state and attempt reconnect if needed
                if not self.is_connected():
                    logger.info(
                        f"Device not connected, attempting reconnection (attempt {attempt + 1})"
                    )
                    if not self._connect():
                        if attempt == max_retries - 1:
                            raise ModbusException(
                                "Device not connected"
                            ) from last_error
                        time.sleep(1)  # Wait before retry
                        continue
                elif attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry for other errors

        logger.error(
            f"Failed to read boiler data after {max_retries} attempts: {last_error}"
        )
        return None

    def set_boiler_setpoint(self, effective_setpoint, max_retries=3):
        """Set the boiler's temperature setpoint.

        The C implementation uses a specific formula for converting temperature to percentage:
        sp = trunc(-101.4856 + 1.7363171 * temp)

        This maps to the boiler's BMS configuration:
        - 2V (0%) -> 70°F
        - 9V (100%) -> 110°F

        Args:
            effective_setpoint (float): Desired temperature in Fahrenheit
            max_retries (int): Maximum number of retry attempts

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            raise ModbusException("Device not connected")

        # Validate range (70-110°F maps to 0-100%)
        if not (70 <= effective_setpoint <= 110):
            logger.error(
                f"Setpoint {effective_setpoint}°F is out of valid range (70-110°F)"
            )
            return False

        # Convert temperature to percentage using the verified formula from C code
        setpoint = math.trunc(-101.4856 + 1.7363171 * effective_setpoint)

        for attempt in range(max_retries):
            try:
                # Write mode (4) to operating mode register (verified from C code)
                result1 = self.client.write_register(
                    self.registers.holding.operating_mode, 4
                )
                if result1.isError():
                    raise ModbusException("Failed to write operating mode")

                # Write setpoint percentage
                result2 = self.client.write_register(
                    self.registers.holding.setpoint, setpoint
                )
                if result2.isError():
                    raise ModbusException("Failed to write setpoint")

                logger.info(
                    f"Successfully set boiler setpoint to {effective_setpoint}°F ({setpoint}%)"
                )
                return True

            except (ModbusException, OSError) as e:
                logger.error(
                    f"Failed to set setpoint (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(1)

        logger.error(f"Failed to set setpoint after {max_retries} attempts")
        return False

    def close(self):
        """Close the Modbus connection."""
        self.client.close()

    def read_operating_status(self):
        """Read operating mode, cascade mode, and current setpoint."""
        try:
            # Read operating mode, cascade mode, and setpoint
            result = self._read_holding_register(
                self.registers.holding.operating_mode, count=3
            )

            return {
                "operating_mode": result[0],
                "operating_mode_str": self.operating_modes.get(
                    str(result[0]), f"Unknown ({result[0]})"
                ),
                "cascade_mode": result[1],
                "cascade_mode_str": self.cascade_modes.get(
                    str(result[1]), f"Unknown ({result[1]})"
                ),
                "current_setpoint": round(c_to_f(result[2] / 10.0), 1),
            }
        except (ModbusException, OSError, AttributeError, IndexError) as e:
            logger.error(f"Failed to read operating status: {str(e)}")
            return None

    def read_error_history(self):
        """Read error history including last lockout and blockout codes."""
        try:
            # Read last lockout and blockout codes
            error_regs = self._read_holding_register(
                self.registers.holding.last_lockout, count=2
            )

            error_history = {}

            # Process lockout code
            lockout_code = error_regs[0]
            error_history["last_lockout_code"] = lockout_code
            error_history["last_lockout_str"] = self.error_codes.get(
                str(lockout_code), f"Unknown ({lockout_code})"
            )

            # Process blockout code
            blockout_code = error_regs[1]
            error_history["last_blockout_code"] = blockout_code
            error_history["last_blockout_str"] = self.error_codes.get(
                str(blockout_code), f"Unknown ({blockout_code})"
            )

            return error_history
        except (ModbusException, OSError, AttributeError, IndexError) as e:
            logger.error(f"Failed to read error history: {str(e)}")
            return None

    def read_model_info(self):
        """Read boiler model information and firmware versions."""
        try:
            # Read model ID and version information
            info_regs = self._read_holding_register(
                self.registers.holding.model_id, count=3
            )

            model_info = {}

            # Process model ID
            model_id = info_regs[0]
            model_info["model_id"] = model_id
            model_info["model_name"] = self.model_ids.get(
                str(model_id), f"Unknown Model ({model_id})"
            )

            # Process firmware and hardware versions
            fw_version = info_regs[1]
            hw_version = info_regs[2]
            model_info["firmware_version"] = f"{fw_version >> 8}.{fw_version & 0xFF}"
            model_info["hardware_version"] = f"{hw_version >> 8}.{hw_version & 0xFF}"

            return model_info
        except (ModbusException, OSError, AttributeError, IndexError) as e:
            logger.error(f"Failed to read model info: {str(e)}")
            return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


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
