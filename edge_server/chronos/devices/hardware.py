"""
Hardware device implementations for interfacing with real physical devices.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Dict

from chronos.config import cfg
from chronos.logging_config import root_logger as logger
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException, ModbusIOException
from serial import Serial


def c_to_f(celsius):
    """Convert Celsius to Fahrenheit."""
    return round((9.0 / 5.0) * celsius + 32.0, 1)


def f_to_c(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return round((fahrenheit - 32.0) * (5.0 / 9.0), 1)


def safe_read_temperature(device_id: str) -> float:
    """Safely read temperature from a device, returning 0 on failure."""
    try:
        path = Path(f"/sys/class/hwmon/{device_id}/temp1_input")
        if not path.exists():
            logger.error(f"Temperature sensor not found at {path}")
            return 0.0

        with open(path, "r") as f:
            temp = int(f.read().strip()) / 1000.0  # Convert from millidegree C to C
            return c_to_f(temp)  # Convert to Fahrenheit
    except (IOError, ValueError) as e:
        logger.error(f"Failed to read temperature from {device_id}: {e}")
        return 0.0


class RelayInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> int:
        """Get the device ID"""
        pass

    @property
    def name(self) -> str:
        """Get the device name, defaults to str(self.id)"""
        return str(self.id)

    @property
    @abstractmethod
    def state(self) -> bool:
        """Get the current device state (True=ON, False=OFF)"""
        pass

    @state.setter
    @abstractmethod
    def state(self, value: bool) -> None:
        """Set the device state"""
        pass


class SerialDevice(RelayInterface):
    """
    Class to handle communication with serial devices.
    This class includes automatic reconnection logic.
    """

    def __init__(
        self, id: int, portname: str = None, baudrate: int = None, name: str = None
    ):
        self._id = id  # Store as private attribute
        self._name = name
        # Handle default values internally
        self.portname = portname if portname is not None else "/dev/ttyUSB0"
        self.baudrate = baudrate if baudrate is not None else 9600
        self._state = None
        self._read_failures = 0
        self._max_read_failures = 5
        self._last_command_time = 0
        self._min_command_interval = 0.1  # seconds
        self.state_to_command = {0: "off", 1: "on"}
        self.command_to_state = {v: k for k, v in self.state_to_command.items()}

    @property
    def id(self) -> int:
        """Get the device ID"""
        return self._id

    @property
    def name(self) -> str:
        """Get the device name"""
        if not self._name:
            self._name = f"Relay {self._id}"
        return self._name

    @property
    def state(self) -> bool:
        """Get the current state of the device."""
        on_off_val = self._send_command(f"relay read {self._id}\n\r")
        # Return last known state if read fails
        if on_off_val is None:
            return False if self._state is None else self._state
        return self.command_to_state[on_off_val]

    @state.setter
    def state(self, value: bool) -> None:
        """Set the state of the device."""
        # Only update if state is changing
        if self.state != value:
            command = self.state_to_command[value]
            self._send_command(f"relay {command} {self._id}\n\r")
            self._state = value
            logger.info(f"Turned device {self._id} {command}")

    def _send_command(self, command: str) -> str:
        """
        Send a command to the device and return the response.
        Handles reconnection and timing logic.
        """
        # Simple rate limiting to avoid flooding the serial port
        current_time = time.time()
        time_since_last = current_time - self._last_command_time
        if time_since_last < self._min_command_interval:
            time.sleep(self._min_command_interval - time_since_last)
        self._last_command_time = time.time()
        try:
            with Serial(
                self.portname, baudrate=self.baudrate, timeout=1, writeTimeout=1
            ) as ser:
                ser.write(command.encode("ascii"))
                # Add a small delay to ensure the device has time to process
                time.sleep(0.1)
                response = ser.readall().decode("ascii")
                return response
        except Exception as e:
            logger.warning(f"Serial port not accessible: {e}")


class ModbusDevice:
    """Class to handle communication with Modbus devices (e.g., boiler controller)."""

    def __init__(self, port: str = None, baudrate: int = None):
        """Initialize the Modbus device with connection parameters."""
        # Set default values if parameters are None
        self.port = port if port is not None else "/dev/ttyUSB1"
        self.baudrate = baudrate if baudrate is not None else 9600

        # Get unit_id from config if available, or default to 1
        try:
            self.device_id = cfg.modbus.unit_id
        except AttributeError:
            self.device_id = 1  # Default Modbus unit ID

        self.client = self._connect()

    def _connect(self):
        """Establish connection to the Modbus device."""
        try:
            client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=1,
            )
            if not client.connect():
                logger.error("Failed to connect to Modbus device")
            return client
        except Exception as e:
            logger.error(f"ModbusDevice initialization error: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.client is not None and self.client.is_socket_open()

    def close(self):
        """Close the connection to the Modbus device."""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()

    def _retry_operation(self, operation, max_retries=2, *args, **kwargs):
        """Retry an operation with exponential backoff."""
        retry_count = 0
        while retry_count <= max_retries:
            try:
                return operation(*args, **kwargs)
            except (ModbusIOException, asyncio.TimeoutError) as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Operation failed after {max_retries} retries: {e}")
                    return None
                backoff_time = 0.5 * (2**retry_count)  # Exponential backoff
                logger.warning(
                    f"Operation failed, retrying in {backoff_time:.1f}s: {e}"
                )
                time.sleep(backoff_time)

    def read_boiler_data(self, max_retries=2):
        """Read all relevant boiler data."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        # Get registers from configuration
        regs = cfg.modbus.registers

        # Read holding registers first (contains configuration data)
        holding_result = self._retry_operation(
            self.client.read_holding_registers,
            max_retries,
            regs.holding.operating_mode,
            7,
            slave=self.device_id,
        )

        # If we couldn't read the holding registers, return None
        if holding_result is None or holding_result.isError():
            return None

        # Read input registers (contains status and sensor data)
        input_result = self._retry_operation(
            self.client.read_input_registers,
            max_retries,
            regs.input.alarm,
            9,
            slave=self.device_id,
        )

        # If we couldn't read the input registers, return None
        if input_result is None or input_result.isError():
            return None

        # Parse the results
        holding_regs = holding_result.registers
        input_regs = input_result.registers

        # Convert register values to human-readable data
        data = {}

        # Modes and status
        data["operating_mode"] = holding_regs[0]  # Operating mode (0-4)
        data["operating_mode_str"] = cfg.modbus.operating_modes.get(
            str(data["operating_mode"]), "Unknown"
        )
        data["cascade_mode"] = holding_regs[1]  # Cascade mode (0-2)
        data["cascade_mode_str"] = cfg.modbus.cascade_modes.get(
            str(data["cascade_mode"]), "Unknown"
        )

        # Temperatures (convert from Celsius x 10 to Fahrenheit)
        # System supply temperature (register 6)
        data["system_supply_temp"] = c_to_f(holding_regs[6] / 10.0)
        # Outlet temperature (register 5)
        data["outlet_temp"] = c_to_f(input_regs[5] / 10.0)
        # Inlet temperature (register 6)
        data["inlet_temp"] = c_to_f(input_regs[6] / 10.0)
        # Flue temperature (register 7)
        data["flue_temp"] = c_to_f(input_regs[7] / 10.0)

        # Status flags
        data["alarm_status"] = bool(input_regs[0])  # Alarm status
        data["pump_status"] = bool(input_regs[1])  # Pump status
        data["flame_status"] = bool(input_regs[2])  # Flame status

        # Power and firing rate
        data["cascade_current_power"] = float(input_regs[3])  # Current power (%)
        data["lead_firing_rate"] = float(input_regs[8])  # Lead firing rate (%)

        return data

    def read_operating_status(self, max_retries=2):
        """Read the current operating status of the boiler."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        status = {}

        # Get data from registers
        regs = cfg.modbus.registers

        # Read operating mode and cascade mode
        result = self._retry_operation(
            self.client.read_holding_registers,
            max_retries,
            regs.holding.operating_mode,
            5,  # Read 5 registers: operating_mode, cascade_mode, setpoint, min, max
            slave=self.device_id,
        )

        if result is None or result.isError():
            return None

        holding_regs = result.registers

        # Read error code
        error_result = self._retry_operation(
            self.client.read_input_registers,
            max_retries,
            regs.input.alarm,
            1,
            slave=self.device_id,
        )

        if error_result is None or error_result.isError():
            return None

        error_code = error_result.registers[0]

        # Parse status
        status["operating_mode"] = holding_regs[0]
        status["operating_mode_str"] = cfg.modbus.operating_modes.get(
            str(status["operating_mode"]), "Unknown"
        )
        status["cascade_mode"] = holding_regs[1]
        status["cascade_mode_str"] = cfg.modbus.cascade_modes.get(
            str(status["cascade_mode"]), "Unknown"
        )

        # Get setpoints (converted to Fahrenheit)
        status["current_setpoint"] = c_to_f(holding_regs[2] / 10.0)

        # Determine overall system status
        if error_code > 0:
            status["status"] = "error"
            status["error_code"] = error_code
            status["error_message"] = cfg.modbus.error_codes.get(
                str(error_code), "Unknown Error"
            )
        elif status["operating_mode"] == 0:  # Initialization
            status["status"] = "initializing"
        elif status["operating_mode"] == 1:  # Standby
            status["status"] = "standby"
        elif status["operating_mode"] in [2, 3, 4]:  # CH, DHW, or Manual
            status["status"] = "running"
        else:
            status["status"] = "unknown"

        return status

    def set_boiler_setpoint(self, temperature: float, max_retries=2) -> bool:
        """Set the boiler setpoint temperature."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        # Validate temperature range
        if temperature < cfg.temperature.min_setpoint:
            logger.error(
                f"Temperature {temperature}°F is below minimum setpoint "
                f"({cfg.temperature.min_setpoint}°F)"
            )
            return False
        if temperature > cfg.temperature.max_setpoint:
            logger.error(
                f"Temperature {temperature}°F is above maximum setpoint "
                f"({cfg.temperature.max_setpoint}°F)"
            )
            return False

        # Convert Fahrenheit to Celsius x 10 for Modbus
        celsius = f_to_c(temperature)
        modbus_value = int(celsius * 10)

        regs = cfg.modbus.registers
        result = self._retry_operation(
            self.client.write_register,
            max_retries,
            regs.holding.setpoint,
            modbus_value,
            slave=self.device_id,
        )

        if result is None or result.isError():
            logger.error(f"Failed to write setpoint: {result}")
            return False

        logger.info(f"Set boiler setpoint to {temperature}°F ({celsius}°C)")
        return True

    def get_temperature_limits(self, max_retries=2) -> Dict[str, float]:
        """Get the current temperature limits."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        regs = cfg.modbus.registers
        result = self._retry_operation(
            self.client.read_holding_registers,
            max_retries,
            regs.holding.min_setpoint,
            2,  # Read min and max
            slave=self.device_id,
        )

        if result is None or result.isError():
            logger.error("Failed to read temperature limits")
            return None

        # Convert Celsius x 10 to Fahrenheit
        min_setpoint = c_to_f(result.registers[0] / 10.0)
        max_setpoint = c_to_f(result.registers[1] / 10.0)

        return {"min_setpoint": min_setpoint, "max_setpoint": max_setpoint}

    def set_temperature_limits(
        self, min_setpoint: float, max_setpoint: float, max_retries=2
    ) -> bool:
        """Set the temperature limits."""
        if not self.is_connected():
            raise ModbusException("Device not connected")

        # Validate input ranges
        if min_setpoint < cfg.temperature.min_setpoint:
            logger.error(
                f"Min setpoint {min_setpoint}°F is below system minimum "
                f"({cfg.temperature.min_setpoint}°F)"
            )
            return False
        if max_setpoint > cfg.temperature.max_setpoint:
            logger.error(
                f"Max setpoint {max_setpoint}°F is above system maximum "
                f"({cfg.temperature.max_setpoint}°F)"
            )
            return False
        if min_setpoint >= max_setpoint:
            logger.error(
                f"Min setpoint {min_setpoint}°F must be less than max setpoint "
                f"{max_setpoint}°F"
            )
            return False

        # Convert Fahrenheit to Celsius x 10 for Modbus
        min_celsius = f_to_c(min_setpoint)
        max_celsius = f_to_c(max_setpoint)
        min_modbus = int(min_celsius * 10)
        max_modbus = int(max_celsius * 10)

        regs = cfg.modbus.registers

        # Write min setpoint
        min_result = self._retry_operation(
            self.client.write_register,
            max_retries,
            regs.holding.min_setpoint,
            min_modbus,
            slave=self.device_id,
        )

        if min_result is None or min_result.isError():
            logger.error(f"Failed to write min setpoint: {min_result}")
            return False

        # Write max setpoint
        max_result = self._retry_operation(
            self.client.write_register,
            max_retries,
            regs.holding.max_setpoint,
            max_modbus,
            slave=self.device_id,
        )

        if max_result is None or max_result.isError():
            logger.error(f"Failed to write max setpoint: {max_result}")
            return False

        logger.info(
            f"Set temperature limits: min={min_setpoint}°F, max={max_setpoint}°F"
        )
        return True


@contextmanager
def create_modbus_connection():
    """Context manager for creating and closing a Modbus connection."""
    device = ModbusDevice(port=cfg.modbus.portname)
    try:
        yield device
    finally:
        device.close()
