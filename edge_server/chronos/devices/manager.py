"""
Device manager abstraction layer for interfacing with hardware.

This module provides a unified interface for managing both relay devices
and Modbus devices.
"""

from typing import Any, Dict, List, Union

from chronos.config import cfg
from chronos.devices.hardware import ModbusDevice, SerialDevice
from chronos.devices.mock import MockModbusDevice, MockSerialDevice
from chronos.logging import root_logger as logger


class RelayManager:
    """Manager for relay devices."""

    def __init__(self):
        """Initialize the relay manager with all configured devices."""
        self._devices = {}

        # Initialize all devices immediately
        # Use the relay dictionary from config which maps names to device IDs
        for relay_name, device_id in cfg.relay.__dict__.items():
            if (
                isinstance(device_id, int) and device_id < 8
            ):  # Only use numeric relay IDs 0-7
                # Pass config values directly, let SerialDevice handle any missing attributes
                self._devices[device_id] = SerialDevice(
                    id=device_id,
                    name=relay_name,
                )
                logger.info(f"Initialized device {device_id} ({relay_name})")

    def get_relay_state(self, device_id: int) -> Dict[str, Any]:
        """Get the current state of a device."""
        if device_id not in self._devices:
            raise ValueError(f"Unknown device ID: {device_id}")

        device = self._devices[device_id]
        return {"id": device_id, "name": device.name, "state": device.state}

    def set_device_state(
        self, device_id: int, state: bool, is_season_switch: bool = False
    ) -> bool:
        """Set the state of a device with safety checks.

        Args:
            device_id: The ID of the device to control
            state: The desired state (True=ON, False=OFF)
            is_season_switch: Whether this is part of a season changeover

        Returns:
            bool: True if successful, False otherwise
        """
        if device_id not in self._devices:
            return False

        # If trying to turn ON a device
        if state:
            # Season switch operations bypass some safety checks
            if not is_season_switch:
                # Rule: Never allow relay 0 (boiler) to be ON with any chiller (relays 1-4)
                if device_id == 0:  # Boiler
                    # Check if any chiller is ON
                    for chiller_id in range(1, 5):
                        if (
                            chiller_id in self._devices
                            and self._devices[chiller_id].state
                        ):
                            logger.warning(
                                "Cannot turn ON boiler while chillers are running"
                            )
                            return False
                elif 1 <= device_id <= 4:  # Chiller
                    # Check if boiler is ON
                    if 0 in self._devices and self._devices[0].state:
                        logger.warning("Cannot turn ON chiller while boiler is running")
                        return False

        # Set state directly if all checks pass
        self._devices[device_id].state = state

        return True

    def get_state_of_all_relays(self) -> List[Dict[str, Any]]:
        """Get the state of all available devices."""
        return [self.get_relay_state(device_id) for device_id in self._devices]


class ModbusManager:
    """Minimal manager for Modbus devices."""

    def __init__(self):
        """Initialize with direct Modbus device connection."""
        # Pass None values, let ModbusDevice handle defaults
        self._modbus = ModbusDevice()

    def get_boiler_stats(self) -> Dict[str, Any]:
        return self._modbus.read_boiler_data()

    def get_operating_status(self) -> Dict[str, Any]:
        return self._modbus.read_operating_status()

    def set_boiler_setpoint(self, temperature: float) -> bool:
        return self._modbus.set_boiler_setpoint(temperature)

    def get_temperature_limits(self) -> Dict[str, float]:
        return self._modbus.get_temperature_limits()

    def set_temperature_limits(self, min_setpoint: float, max_setpoint: float) -> bool:
        return self._modbus.set_temperature_limits(min_setpoint, max_setpoint)

    def get_sensor_data(self) -> Dict[str, Any]:
        """Get sensor data - stub implementation for API compatibility."""
        return {}


class DeviceManager(RelayManager, ModbusManager):
    """Unified manager for all device types."""

    def __init__(self):
        """Initialize both relay and Modbus managers."""
        RelayManager.__init__(self)
        ModbusManager.__init__(self)
        logger.info("Initialized device manager with relay and Modbus support")

    def is_mock_mode(self) -> bool:
        """Check if the system is in mock mode."""
        return False


class MockRelayManager(RelayManager):
    """Mock implementation of RelayManager."""

    def __init__(self):
        """Initialize the mock relay manager with all configured devices."""
        self._devices = {}

        # Initialize mock devices for each configured relay
        for relay_name, device_id in cfg.relay.__dict__.items():
            if (
                isinstance(device_id, int) and device_id < 8
            ):  # Only use numeric relay IDs 0-7
                self._devices[device_id] = MockSerialDevice(
                    id=device_id, name=relay_name
                )
                logger.info(f"Initialized mock device {device_id} ({relay_name})")


class MockModbusManager(ModbusManager):
    """Mock implementation of ModbusManager."""

    def __init__(self):
        """Initialize with mock Modbus device."""
        self._modbus = MockModbusDevice()

    def get_boiler_stats(self) -> Dict[str, Any]:
        return self._modbus.read_boiler_data()

    def get_operating_status(self) -> Dict[str, Any]:
        return self._modbus.read_operating_status()

    def set_boiler_setpoint(self, temperature: float) -> bool:
        return self._modbus.set_boiler_setpoint(temperature)

    def get_sensor_data(self) -> Dict[str, Any]:
        """Get readings from sensors."""
        # Create simulated sensor readings using the Modbus device's methods
        boiler_data = self._modbus.read_boiler_data()
        return {
            "cpu_temp": 70.0,
            "ambient_temp": 72.0,
            "inlet_temp": boiler_data.get("inlet_temp", 120.0),
            "outlet_temp": boiler_data.get("outlet_temp", 140.0),
            "return_temp": boiler_data.get("inlet_temp", 120.0),
            "water_out_temp": boiler_data.get("outlet_temp", 140.0),
        }


class MockDeviceManager(MockRelayManager, MockModbusManager):
    """Mock implementation of DeviceManager for testing."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            MockRelayManager.__init__(self)
            MockModbusManager.__init__(self)
            logger.info("Initialized mock device manager")
            self._initialized = True

    def is_mock_mode(self) -> bool:
        return True


def get_device_manager() -> Union[DeviceManager, MockDeviceManager]:
    """Get the appropriate device manager instance.

    Returns a MockDeviceManager if MOCK_DEVICES is True, otherwise returns a real DeviceManager.
    """
    if cfg.MOCK_DEVICES:
        logger.info("Initializing MockDeviceManager")
        return MockDeviceManager()
    else:
        logger.info("Initializing real DeviceManager")
        return DeviceManager()
