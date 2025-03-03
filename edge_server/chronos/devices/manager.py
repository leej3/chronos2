"""
Device manager abstraction layer for interfacing with hardware.

This module provides a unified interface for managing both relay devices
and Modbus devices.
"""

from datetime import UTC, timedelta
from typing import Any, Dict, List, Union

from apscheduler.schedulers.background import BackgroundScheduler
from chronos.config import cfg
from chronos.devices.hardware import ModbusDevice, SerialDevice
from chronos.devices.mock import MockModbusDevice, MockSerialDevice
from chronos.logging_config import root_logger as logger
from chronos.utils import get_current_time


class RelayManager:
    """Manager for relay devices."""

    def __init__(self, season_mode="winter"):
        """Initialize the relay manager with all configured devices."""
        self._devices = {}
        self._season_mode = None
        self.season_mode = season_mode
        self.is_switching_season = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
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

        # Init season mode based on summer/winter valve
        self.season_mode = "winter" if self.get_relay_state(5)["state"] else "summer"

    @property
    def season_mode(self):
        return self._season_mode

    @season_mode.setter
    def season_mode(self, value):
        if value not in {"winter", "summer"}:
            raise ValueError("season_mode must be either 'winter' or 'summer'")
        self._season_mode = value

    def get_relay_state(self, device_id: int) -> Dict[str, Any]:
        """Get the current state of a device."""
        if device_id not in self._devices:
            raise ValueError(f"Unknown device ID: {device_id}")

        device = self._devices[device_id]
        return {
            "id": device_id,
            "name": device.name,
            "state": device.state,
        }

    def _validate_update_boiler(self, state: bool) -> bool:
        """
        - Cannot turn ON boiler when season_mode = "summer"
        - Cannot turn ON boiler while chillers are running
        - Cannot turn ON boiler while summer valve is ON
        """
        if self.season_mode == "summer" and state:
            raise ValueError("Cannot turn ON boiler when season_mode = 'summer'")

        for chiller_id in range(1, 5):
            if (
                chiller_id in self._devices
                and self._devices[chiller_id].state
                and state
            ):
                raise ValueError("Cannot turn ON boiler while chillers are running")

        if state and self.get_relay_state(6)["state"]:
            raise ValueError("Cannot turn ON boiler while summer valve is ON")
        return True

    def _validate_update_chiller(self, state: bool) -> bool:
        """
        - Cannot turn ON chiller when season_mode = "winter"
        - Cannot turn ON chiller while boiler is running
        - Cannot turn ON chiller while winter valve is ON
        """
        if self.season_mode == "winter" and state:
            raise ValueError("Cannot turn ON chiller when season_mode = 'winter'")
        if state and self.get_relay_state(0)["state"]:
            raise ValueError("Cannot turn ON chiller while boiler is running")
        if state and self.get_relay_state(5)["state"]:
            raise ValueError("Cannot turn ON chiller while winter valve is ON")
        return True

    def _validate_update_summer_valve(self, state: bool) -> bool:
        """
        - Cannot turn ON summer valve when season_mode = "winter".
        - Cannot turn ON summer valve while winter valve is ON
        """
        if self.season_mode == "winter" and state:
            raise ValueError("Cannot turn ON summer/winter valve in winter mode")
        if state and self.get_relay_state(5)["state"]:
            raise ValueError("Cannot turn ON summer valve while winter valve is ON")
        return True

    def _validate_update_winter_valve(self, state: bool) -> bool:
        """
        - Cannot turn ON winter valve when season_mode = "summer".
        - Cannot turn ON winter valve while summer valve is ON
        """
        if self.season_mode == "summer" and state:
            raise ValueError("Cannot turn ON winter/summer valve in summer mode")
        if state and self.get_relay_state(6)["state"]:
            raise ValueError("Cannot turn ON winter valve while summer valve is ON")
        return True

    def set_device_state(self, device_id: int, state: bool) -> bool:
        """Set the state of a device with safety checks.

        Args:
            device_id: The ID of the device to control
            state: The desired state (True=ON, False=OFF)

        Returns:
            bool: True if successful, False otherwise
        """
        if cfg.READ_ONLY_MODE:
            raise ValueError("Cannot set device state in read-only mode")

        if device_id not in self._devices:
            return False

        if device_id == 0:
            self._validate_update_boiler(state)
        elif 1 <= device_id <= 4:
            self._validate_update_chiller(state)
        elif device_id == 5:
            self._validate_update_winter_valve(state)
        elif device_id == 6:
            self._validate_update_summer_valve(state)

        # Set state directly if all checks pass
        self._devices[device_id].state = state

        return True

    def get_state_of_all_relays(self) -> List[Dict[str, Any]]:
        """Get the state of all available devices."""
        return [self.get_relay_state(device_id) for device_id in self._devices]

    def _turn_off_all_devices(self):
        for device in self._devices.values():
            self.set_device_state(device.id, False)

    def season_switch(self, season_mode: str, mode_switch_lockout_time: int):
        """Handle season switching logic for relays."""
        if season_mode == "winter":
            logger.debug("Switching to winter mode")
            self.season_mode = "winter"
            self._turn_off_all_devices()
            self._turn_off_device(6)
            self._turn_on_device(5)
            self.scheduler.add_job(
                self._restore_devices_state_for_winter,
                "date",
                run_date=self.get_current_time()
                + timedelta(minutes=mode_switch_lockout_time),
            )
            self.is_switching_season = True

        elif season_mode == "summer":
            logger.debug("Switching to summer mode")
            self.season_mode = "summer"
            self._turn_off_all_devices()
            self._turn_off_device(5)
            self._turn_on_device(6)
            self.scheduler.add_job(
                self._restore_devices_state_for_summer,
                "date",
                run_date=self.get_current_time()
                + timedelta(minutes=mode_switch_lockout_time),
            )
            self.is_switching_season = True

    def _restore_devices_state_for_winter(self):
        self._turn_on_device(0)
        self.is_switching_season = False

    def _restore_devices_state_for_summer(self):
        self._turn_on_device(1)
        self._turn_on_device(2)
        self._turn_on_device(3)
        self._turn_on_device(4)
        self.is_switching_season = False

    def _turn_off_device(self, relay_id: int):
        self.set_device_state(relay_id, False)

    def _turn_on_device(self, relay_id: int):
        self.set_device_state(relay_id, True)

    def get_current_time(self):
        return get_current_time(UTC)


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

    def __init__(self, season_mode="winter"):
        """Initialize the mock relay manager with all configured devices."""
        self._devices = {}
        self._season_mode = None
        self.season_mode = season_mode
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.is_switching_season = False

        # Initialize mock devices for each configured relay
        for relay_name, device_id in cfg.relay.__dict__.items():
            if (
                isinstance(device_id, int) and device_id < 8
            ):  # Only use numeric relay IDs 0-7
                self._devices[device_id] = MockSerialDevice(
                    id=device_id, name=relay_name
                )
                logger.info(f"Initialized mock device {device_id} ({relay_name})")

        # Init season mode based on summer/winter valve
        self.season_mode = "winter" if self.get_relay_state(5)["state"] else "summer"


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
