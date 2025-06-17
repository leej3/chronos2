"""
Device management abstraction layer for Chronos.

This module provides a unified interface for accessing and controlling
both real hardware devices and mock implementations for testing and development.
"""

# Import public classes and functions from our submodules
from chronos.devices.hardware import (
    ModbusDevice,
    ModbusException,
    SerialDevice,
    create_modbus_connection,
    safe_read_temperature,
)
from chronos.devices.manager import DeviceManager, MockDeviceManager, get_device_manager
from chronos.devices.mock import MockModbusDevice, MockSerialDevice

# Define what should be accessible when `from chronos.devices import *` is used
__all__ = [
    # Main device manager interface
    "DeviceManager",
    "MockDeviceManager",
    "get_device_manager",
    # Specific implementations (for direct access if needed)
    "MockSerialDevice",
    "MockModbusDevice",
    # Hardware interfaces
    "ModbusDevice",
    "ModbusException",
    "SerialDevice",
    "create_modbus_connection",
    "safe_read_temperature",
]
