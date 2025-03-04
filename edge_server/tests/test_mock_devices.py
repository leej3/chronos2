import time
from unittest.mock import patch

import pytest
from chronos.config import cfg
from chronos.devices.manager import (
    MockDeviceManager,
    MockModbusManager,
    MockRelayManager,
    get_device_manager,
)
from chronos.devices.mock import MockModbusDevice, MockSerialDevice


@pytest.fixture(autouse=True)
def mock_mode():
    """Ensure mock mode is enabled for these tests."""
    original = cfg.MOCK_DEVICES
    cfg.MOCK_DEVICES = True
    yield
    cfg.MOCK_DEVICES = original


@pytest.fixture
def mock_device_manager():
    """Return a MockDeviceManager instance."""
    return MockDeviceManager()


@pytest.fixture
def mock_relay_manager():
    """Return a MockRelayManager instance."""
    manager = MockRelayManager()
    manager.is_switching_season = False
    return manager


@pytest.fixture
def mock_modbus_manager():
    """Return a MockModbusManager instance."""
    manager = MockModbusManager()
    return manager


@pytest.fixture
def mock_modbus_device():
    """Return a MockModbusDevice instance."""
    manager = MockModbusDevice(port="COM1", baudrate=9600)
    return manager


@pytest.fixture
def mock_serial_device():
    """Return a MockSerialDevice instance."""
    manager = MockSerialDevice()
    return manager


def test_mock_device_manager_singleton():
    """Test that MockDeviceManager is a singleton."""
    # Ensure mock mode is enabled
    cfg.MOCK_DEVICES = True

    manager1 = MockDeviceManager()
    manager2 = get_device_manager()

    assert manager1 == manager2
    assert isinstance(manager1, MockDeviceManager)
    assert isinstance(manager2, MockDeviceManager)


def test_device_state_tracking(mock_relay_manager):
    """Test that device state changes are tracked."""
    manager = mock_relay_manager
    manager.season_mode = "winter"
    # turn off all devices
    for i in range(5):
        manager.set_device_state(i, False)
    # get all devices
    devices = manager.get_state_of_all_relays()
    # check that all devices are off
    for i in range(5):
        assert devices[i]["state"] == 0

    # turn on boiler
    manager.season_mode = "winter"
    manager.set_device_state(0, True)
    device = manager.get_relay_state(0)
    assert device["state"] == 1

    # turn on  all chiller
    manager.season_mode = "summer"
    manager.set_device_state(0, False)
    manager.set_device_state(1, True)
    manager.set_device_state(2, True)
    manager.set_device_state(3, True)
    manager.set_device_state(4, True)
    devices = manager.get_state_of_all_relays()
    for i in range(1, 4):
        assert devices[i]["state"] == 1


def test_device_state_validation(mock_relay_manager):
    """Test that device state validation works."""
    manager = mock_relay_manager
    manager.season_mode = "summer"
    with pytest.raises(
        ValueError, match="Cannot turn ON boiler when season_mode = 'summer'"
    ):
        manager.set_device_state(0, True)

    manager.season_mode = "winter"
    with pytest.raises(
        ValueError, match="Cannot turn ON chiller when season_mode = 'winter'"
    ):
        manager.set_device_state(1, True)

    with pytest.raises(
        ValueError, match="Cannot turn ON chiller when season_mode = 'winter'"
    ):
        manager.set_device_state(2, True)


def test_summer_valve_validation(mock_relay_manager):
    """Test that summer valve validation works."""
    manager = mock_relay_manager
    manager.season_mode = "summer"
    with pytest.raises(
        ValueError, match="Cannot turn ON winter/summer valve in summer mode"
    ):
        manager.set_device_state(5, True)

    manager.season_mode = "winter"
    with pytest.raises(
        ValueError, match="Cannot turn ON summer/winter valve in winter mode"
    ):
        manager.set_device_state(6, True)


def test_invalid_device_id(mock_relay_manager):
    """Test handling of invalid device IDs."""
    manager = mock_relay_manager

    with pytest.raises(ValueError, match="Unknown device ID: 10"):
        manager.get_relay_state(10)


def test_boiler_setpoint_tracking(mock_modbus_manager):
    """Test that setpoint changes are tracked."""
    manager = mock_modbus_manager

    current_setpoint = 95.0

    manager.set_boiler_setpoint(current_setpoint)

    assert manager.get_operating_status()["current_setpoint"] == current_setpoint


def test_boiler_setpoint_validation(mock_modbus_manager):
    """Test setpoint validation."""
    manager = mock_modbus_manager
    temperature_below_minimum = 60.0
    temperature_above_maximum = 120.0
    # Test setting a setpoint below minimum
    with pytest.raises(
        ValueError, match=f"Temperature {temperature_below_minimum}°F is below minimum"
    ):
        manager.set_boiler_setpoint(temperature_below_minimum)

    # Test setting a setpoint above maximum
    with pytest.raises(
        ValueError, match=f"Temperature {temperature_above_maximum}°F is above maximum"
    ):
        manager.set_boiler_setpoint(temperature_above_maximum)


def test_temperature_limits(mock_device_manager):
    """Test setting temperature limits."""
    manager = mock_device_manager

    # Save original limits

    # Set new valid limits
    manager.season_mode = "winter"
    manager.set_temperature_limits(75.0, 105.0)
    assert manager.get_temperature_limits()["min_setpoint"] == 75.0
    assert manager.get_temperature_limits()["max_setpoint"] == 105.0

    # Test validation of invalid limits
    with pytest.raises(
        ValueError,
        match="Minimum setpoint 90.0°F must be less than maximum setpoint 85.0°F",
    ):
        manager.set_temperature_limits(90.0, 85.0)

    with pytest.raises(
        ValueError,
        match="Temperature limits 65.0°F and 105.0°F are outside allowed range",
    ):
        manager.set_temperature_limits(65.0, 105.0)


def test_device_status(mock_relay_manager):
    """Test that device status reflects state changes."""
    manager = mock_relay_manager
    manager.season_mode = "winter"
    # Set boiler state to on
    manager.set_device_state(0, True)
    assert manager.get_relay_state(0)["state"] == 1
    assert manager.get_relay_state(0)["name"] == "boiler"
    assert manager.get_relay_state(0)["id"] == 0

    manager.season_mode = "summer"
    # Set boiler state to off
    manager.set_device_state(1, False)
    assert manager.get_relay_state(1)["state"] == 0
    assert manager.get_relay_state(1)["name"] == "chiller2"
    assert manager.get_relay_state(1)["id"] == 1


def test_boiler_stats_integration(mock_modbus_manager, mock_relay_manager):
    """Test that boiler stats reflect device state."""
    modbus_manager = mock_modbus_manager
    relay_manager = mock_relay_manager
    # Set boiler state to on
    relay_manager.season_mode = "winter"
    relay_manager.set_device_state(0, True)
    stats = modbus_manager.get_boiler_stats()
    assert stats["pump_status"] in [True, False]
    assert stats["flame_status"] in [True, False]

    # Set boiler state to off
    relay_manager.season_mode = "summer"
    relay_manager.set_device_state(1, False)
    stats = modbus_manager.get_boiler_stats()
    assert stats["pump_status"] in [True, False]
    assert stats["flame_status"] in [True, False]


def test_operating_status_integration(
    mock_modbus_manager, mock_relay_manager, mock_modbus_device
):
    """Test that operating status reflects device state."""
    modbus_manager = mock_modbus_manager
    relay_manager = mock_relay_manager
    modbus_device = mock_modbus_device
    relay_manager.season_mode = "winter"
    # Set operating mode to running
    modbus_device._operating_mode = 2
    with patch(
        "chronos.devices.mock.MockModbusDevice.read_operating_status",
        return_value={"status": "running"},
    ):
        relay_manager.set_device_state(0, True)
        status = modbus_manager.get_operating_status()
        assert status["status"] == "running"

    # Set boiler state to off
    relay_manager.season_mode = "winter"
    with patch(
        "chronos.devices.mock.MockModbusDevice.read_operating_status",
        return_value={"status": "idle"},
    ):
        relay_manager.set_device_state(0, False)
        status = modbus_manager.get_operating_status()
        assert status["status"] in ["idle", "off"]


def test_season_switch(mock_relay_manager):
    manager = mock_relay_manager

    """Test that season switch works."""
    # Winter -> summer
    manager.season_mode = "winter"
    manager.season_switch("summer", 10)
    assert manager.get_relay_state(5)["state"] == 0
    assert manager.get_relay_state(6)["state"] == 1
    assert manager.season_mode == "summer"
    time.sleep(10)

    # Summer -> winter
    manager.season_switch("winter", 10)
    assert manager.get_relay_state(5)["state"] == 1
    assert manager.get_relay_state(6)["state"] == 0
    assert manager.season_mode == "winter"
    time.sleep(10)
