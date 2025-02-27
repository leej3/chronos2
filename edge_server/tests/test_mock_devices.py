import pytest
from chronos.mock_devices.mock_data import (
    MockDeviceManager,
    get_mock_device_manager,
    mock_boiler_stats,
    mock_devices_state,
    mock_operating_status,
)


def test_mock_device_manager_singleton():
    """Test that MockDeviceManager is a singleton."""
    manager1 = MockDeviceManager()
    manager2 = MockDeviceManager()

    # Verify they are the same instance
    assert manager1 is manager2

    # Verify get_mock_device_manager returns the same instance
    manager3 = get_mock_device_manager()
    assert manager1 is manager3


def test_device_state_tracking():
    """Test that device state changes are tracked."""
    manager = get_mock_device_manager()

    # Reset to known state
    for i in range(5):
        manager.set_device_state(i, False)

    # Initial state should be all False
    for i in range(5):
        assert not manager.get_relay_state(i)

    # Change device 0 to True
    manager.set_device_state(0, True)

    # Verify device 0 is now True
    assert manager.get_relay_state(0)

    # Other devices should still be False
    for i in range(1, 5):
        assert not manager.get_relay_state(i)

    # Verify mock_devices_state() reflects the changes
    devices = mock_devices_state()
    assert devices[0]["state"] == 1
    for i in range(1, 5):
        assert devices[i]["state"] == 0


def test_invalid_device_id():
    """Test handling of invalid device IDs."""
    manager = get_mock_device_manager()

    with pytest.raises(ValueError, match="Invalid device ID: 10"):
        manager.get_relay_state(10)

    with pytest.raises(ValueError, match="Invalid device ID: -1"):
        manager.set_device_state(-1, True)


def test_setpoint_tracking():
    """Test that setpoint changes are tracked."""
    manager = get_mock_device_manager()

    # Set a new setpoint
    initial_setpoint = manager.current_setpoint
    new_setpoint = 95.0

    manager.set_setpoint(new_setpoint)

    # Verify the setpoint was updated
    assert manager.current_setpoint == new_setpoint

    # Verify mock_operating_status() returns the new setpoint
    status = mock_operating_status()
    assert status["current_setpoint"] == new_setpoint
    assert status["setpoint_temperature"] == new_setpoint

    # Reset to initial setpoint
    manager.set_setpoint(initial_setpoint)


def test_setpoint_validation():
    """Test setpoint validation."""
    manager = get_mock_device_manager()

    # Test setting a valid setpoint
    assert manager.set_setpoint(90.0)

    # Test setting a setpoint below minimum
    with pytest.raises(ValueError, match="outside allowed range"):
        manager.set_setpoint(60.0)

    # Test setting a setpoint above maximum
    with pytest.raises(ValueError, match="outside allowed range"):
        manager.set_setpoint(120.0)


def test_temperature_limits():
    """Test setting temperature limits."""
    manager = get_mock_device_manager()

    # Save original limits
    original_min = manager.min_setpoint
    original_max = manager.max_setpoint

    try:
        # Set new valid limits
        manager.set_temperature_limits(75.0, 105.0)
        assert manager.min_setpoint == 75.0
        assert manager.max_setpoint == 105.0

        # Set a setpoint at the new minimum
        assert manager.set_setpoint(75.0)

        # Set a setpoint at the new maximum
        assert manager.set_setpoint(105.0)

        # Test validation of invalid limits
        with pytest.raises(
            ValueError, match="Min setpoint must be less than max setpoint"
        ):
            manager.set_temperature_limits(90.0, 85.0)

        with pytest.raises(ValueError, match="out of allowed range"):
            manager.set_temperature_limits(65.0, 105.0)

        with pytest.raises(ValueError, match="out of allowed range"):
            manager.set_temperature_limits(75.0, 115.0)
    finally:
        # Restore original limits
        manager.set_temperature_limits(original_min, original_max)


def test_boiler_stats_integration():
    """Test that boiler stats reflect device state."""
    manager = get_mock_device_manager()

    # Set boiler state to on
    manager.set_device_state(0, True)
    stats = mock_boiler_stats()
    assert stats["pump_status"] is True
    assert stats["flame_status"] is True

    # Set boiler state to off
    manager.set_device_state(0, False)
    stats = mock_boiler_stats()
    assert stats["pump_status"] is False
    assert stats["flame_status"] is False


def test_operating_status_integration():
    """Test that operating status reflects device state."""
    manager = get_mock_device_manager()

    # Set boiler state to on
    manager.set_device_state(0, True)
    status = mock_operating_status()
    assert status["status"] == "running"

    # Set boiler state to off
    manager.set_device_state(0, False)
    status = mock_operating_status()
    assert status["status"] in ["idle", "off"]
