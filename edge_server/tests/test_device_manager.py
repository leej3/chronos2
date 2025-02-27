from unittest.mock import MagicMock, patch

import pytest
from chronos.device_manager import (
    MockDeviceManager,
    RealDeviceManager,
    get_device_manager,
)


def test_get_device_manager_mock():
    """Test that get_device_manager returns a MockDeviceManager when MOCK_DEVICES is True."""
    with patch("chronos.devices.device_manager.cfg") as mock_cfg:
        mock_cfg.MOCK_DEVICES = True
        manager = get_device_manager()
        assert isinstance(manager, MockDeviceManager)


def test_get_device_manager_real():
    """Test that get_device_manager returns a RealDeviceManager when MOCK_DEVICES is False."""
    with patch("chronos.devices.device_manager.cfg") as mock_cfg:
        mock_cfg.MOCK_DEVICES = False
        # Need to mock SerialDevice to avoid actual hardware access
        with patch("chronos.devices.device_manager.SerialDevice"):
            manager = get_device_manager()
            assert isinstance(manager, RealDeviceManager)


class TestMockDeviceManager:
    def test_device_state_management(self):
        """Test that MockDeviceManager correctly manages device states."""
        manager = MockDeviceManager()

        # Set device states
        for i in range(5):
            manager.set_device_state(i, False)

        # Verify states are all False
        for i in range(5):
            assert not manager.get_relay_state(i)

        # Change one state
        manager.set_device_state(0, True)
        assert manager.get_relay_state(0)

        # Check all device states
        devices = manager.get_state_of_all_relays()
        assert len(devices) == 5
        assert devices[0]["state"] is True
        for i in range(1, 5):
            assert devices[i]["state"] is False

    def test_switch_state(self):
        """Test switch_state functionality."""
        manager = MockDeviceManager()

        # Switch on
        manager.switch_state("on", False)
        assert manager.get_relay_state(0)

        # Switch off
        manager.switch_state("off", False)
        assert not manager.get_relay_state(0)

    def test_boiler_setpoint(self):
        """Test boiler setpoint management."""
        manager = MockDeviceManager()

        # Initial state should have a valid setpoint
        initial_setpoint = manager.mock_state.current_setpoint
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
        """Create a RealDeviceManager with mocked dependencies."""
        with patch("chronos.devices.device_manager.SerialDevice") as mock_serial:
            mock_serial.side_effect = mock_serial_devices
            manager = RealDeviceManager()
            # Replace real devices with mocks
            manager.devices = mock_serial_devices
            yield manager

    def test_device_state_management(self, manager, mock_serial_devices):
        """Test that RealDeviceManager correctly manages device states."""
        # Set device states
        for i in range(5):
            manager.set_device_state(i, False)
            mock_serial_devices[i].state = False

        # Verify states are all False
        for i in range(5):
            assert not manager.get_relay_state(i)

        # Change one state
        manager.set_device_state(0, True)
        mock_serial_devices[0].state = True
        assert manager.get_relay_state(0)

        # Check all device states
        devices = manager.get_state_of_all_relays()
        assert len(devices) == 5
        assert devices[0]["state"] is True
        for i in range(1, 5):
            assert devices[i]["state"] is False

    def test_switch_state(self, manager, mock_serial_devices):
        """Test switch_state functionality."""
        # Setup mock
        mock_serial_devices[0].switch_state.return_value = True

        # Call method
        result = manager.switch_state("on", False)

        # Verify mock was called
        mock_serial_devices[0].switch_state.assert_called_with("on", False)
        assert result is True

    def test_boiler_stats(self, manager):
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

        with patch(
            "chronos.devices.device_manager.create_modbus_connection"
        ) as mock_create:
            mock_device = MagicMock()
            mock_device.__enter__.return_value.read_boiler_data.return_value = (
                mock_stats
            )
            mock_create.return_value = mock_device

            stats = manager.get_boiler_stats()
            assert stats == mock_stats

    def test_operating_status(self, manager):
        """Test operating status with mocked ModbusDevice."""
        mock_status = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": 90.0,
        }

        with patch(
            "chronos.devices.device_manager.create_modbus_connection"
        ) as mock_create:
            mock_device = MagicMock()
            mock_device.__enter__.return_value.read_operating_status.return_value = (
                mock_status
            )
            mock_create.return_value = mock_device

            status = manager.get_operating_status()
            assert status == mock_status

    def test_validation(self, manager):
        """Test validation in the real manager."""
        # Invalid device ID
        with pytest.raises(ValueError):
            manager.get_relay_state(10)

        # Test error propagation from modbus device
        with patch(
            "chronos.devices.device_manager.create_modbus_connection"
        ) as mock_create:
            mock_device = MagicMock()
            mock_device.__enter__.return_value.set_boiler_setpoint.return_value = False
            mock_create.return_value = mock_device

            with pytest.raises(RuntimeError, match="Failed to set temperature"):
                manager.set_boiler_setpoint(90.0)
