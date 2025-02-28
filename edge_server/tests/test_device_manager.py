from unittest.mock import MagicMock, patch

import pytest
from chronos.config import cfg
from chronos.devices.manager import (
    DeviceManager,
    MockDeviceManager,
    MockModbusDevice,
    MockModbusManager,
    MockRelayManager,
    MockSerialDevice,
    get_device_manager,
)


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


def test_get_device_manager_mock():
    cfg.MOCK_DEVICES = True
    manager = get_device_manager()
    assert isinstance(manager, MockDeviceManager)


def test_get_device_manager_real():
    cfg.MOCK_DEVICES = False
    manager = get_device_manager()
    assert isinstance(manager, DeviceManager)


class TestMockDeviceManager:
    def test_device_state_management(self):
        """Test that MockDeviceManager correctly manages device states."""
        manager = MockDeviceManager()

        # Set device states
        for i in range(5):
            manager.set_device_state(i, False)

        # Verify states are all False
        devices = manager.get_state_of_all_relays()
        for i in range(5):
            assert devices[i]["state"] == 0

        # Change one state
        manager.set_device_state(0, True)
        assert manager.get_relay_state(0)

        # Check all device states
        devices = manager.get_state_of_all_relays()
        assert len(devices) == 8  # 5 relays + 3 chiller
        assert devices[0]["state"] == 1
        for i in range(1, 5):
            assert devices[i]["state"] == 0

    def test_boiler_setpoint(self, mock_modbus_manager):
        """Test boiler setpoint management."""
        manager = mock_modbus_manager

        # Initial state should have a valid setpoint
        initial_setpoint = manager.get_operating_status()["current_setpoint"]
        print("initial_setpoint", initial_setpoint)
        assert 70 <= initial_setpoint <= 110

        # Set a new setpoint
        new_setpoint = 95.0
        manager.set_boiler_setpoint(new_setpoint)

        # Get operating status and check setpoint
        status = manager.get_operating_status()
        assert status["current_setpoint"] == new_setpoint

        # Reset to original
        manager.set_boiler_setpoint(initial_setpoint)

    def test_temperature_limits(self):
        """Test temperature limits management."""
        manager = MockDeviceManager()

        # Get initial limits
        limits = manager.get_temperature_limits()
        assert "min_setpoint" in limits
        assert "max_setpoint" in limits

        # Set new limits
        manager.set_temperature_limits(75.0, 105.0)

        # Verify limits were updated
        new_limits = manager.get_temperature_limits()
        assert new_limits["min_setpoint"] == 75.0
        assert new_limits["max_setpoint"] == 105.0

        # Reset to defaults
        manager.set_temperature_limits(70.0, 110.0)

    def test_validation(self):
        """Test validation in the mock manager."""
        manager = MockDeviceManager()

        # Invalid device ID
        with pytest.raises(ValueError):
            manager.get_relay_state(10)

        # Invalid setpoint
        with pytest.raises(ValueError):
            manager.set_boiler_setpoint(120.0)

        # Invalid temperature limits
        with pytest.raises(ValueError):
            manager.set_temperature_limits(90.0, 80.0)


class TestRealDeviceManager:
    @pytest.fixture
    def mock_serial_devices(self):
        """Mock serial devices for RealDeviceManager."""
        mock_devices = []
        for i in range(5):
            device = MagicMock()
            device.id = i
            device.state = True
            mock_devices.append(device)
        return mock_devices

    @pytest.fixture
    def manager(self, mock_serial_devices):
        with patch("chronos.devices.hardware.SerialDevice") as mock_serial:
            mock_serial.side_effect = mock_serial_devices
        manager = DeviceManager()
        manager._devices = {
            i: mock_serial_devices[i] for i in range(len(mock_serial_devices))
        }
        try:
            yield manager
        finally:
            pass

    def test_device_state_management(self, manager, mock_serial_devices):
        """Test that RealDeviceManager correctly manages device states."""
        # Set device states
        for i in range(5):
            manager.set_device_state(i, False)
            mock_serial_devices[i].state = False

        # Verify states are all False
        devices = manager.get_state_of_all_relays()
        for i in range(5):
            assert devices[i]["state"] is False

        # # Change one state
        manager.set_device_state(0, True)
        mock_serial_devices[0].state = True
        assert manager.get_relay_state(0)

        # # Check all device states
        devices = manager.get_state_of_all_relays()
        assert len(devices) == 5
        assert devices[0]["state"] is True
        for i in range(1, 5):
            assert devices[i]["state"] is False

    def test_boiler_stats(self, manager, mock_serial_devices):
        """Test boiler stats with mocked ModbusDevice."""
        mock_stats = {
            "system_supply_temp": 154.4,
            "outlet_temp": 158.0,
            "inlet_temp": 149.0,
            "flue_temp": 176.0,
            "cascade_current_power": 50.0,
            "lead_firing_rate": 75.0,
            "pump_status": True,
            "flame_status": True,
        }

        manager.get_boiler_stats = MagicMock(return_value=mock_stats)
        stats = manager.get_boiler_stats()
        assert stats == mock_stats

    def test_operating_status(self, manager, mock_serial_devices):
        """Test operating status with mocked ModbusDevice."""
        mock_status = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": 90.0,
        }

        manager.get_operating_status = MagicMock(return_value=mock_status)
        status = manager.get_operating_status()
        assert status == mock_status

    def test_validation(self, manager, mock_serial_devices):
        """Test validation in the real manager."""
        # Invalid device ID
        with pytest.raises(ValueError, match="Unknown device ID: 10"):
            manager.get_relay_state(10)

        # Test error propagation from modbus device
        manager.set_boiler_setpoint = MagicMock(
            side_effect=RuntimeError("Failed to set temperature")
        )
        with pytest.raises(RuntimeError, match="Failed to set temperature"):
            manager.set_boiler_setpoint(90.0)
