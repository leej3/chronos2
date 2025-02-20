import logging
import os
from unittest.mock import patch

import pytest
from chronos.config import cfg
from chronos.devices import ModbusDevice, ModbusException

logger = logging.getLogger(__name__)


# Test data for parametrized tests
VALID_SETPOINTS = [
    (70.0, "minimum valid temperature"),
    (90.0, "typical operating temperature"),
    (110.0, "maximum valid temperature"),
]

INVALID_SETPOINTS = [
    (69.9, "below minimum"),
    (110.1, "above maximum"),
    (0.0, "zero temperature"),
    (-10.0, "negative temperature"),
]

ERROR_SCENARIOS = [
    (ModbusException("Connection failed"), 500, "Connection failed"),
    (ModbusException("Timeout"), 500, "Timeout"),
    (ValueError("Invalid response"), 500, "Invalid response"),
    (RuntimeError("Unknown error"), 500, "Unknown error"),
]


def is_modbus_connected():
    try:
        with ModbusDevice(port=cfg.modbus.portname) as device:
            return device.is_connected()
    except Exception as e:
        logger.error(f"Error connecting to modbus device: {e}")
        return False


# Legacy endpoint tests
def test_get_data(client, mock_temperature_sensor, mock_serial_devices):
    """Test the legacy get_data endpoint."""
    response = client.get("/get_data")
    assert response.status_code == 200
    data = response.json()

    assert "sensors" in data
    assert "devices" in data
    assert isinstance(data["sensors"]["water_out_temp"], (int, float))
    assert isinstance(data["sensors"]["return_temp"], (int, float))
    assert data["mock_devices"] in [True, False]
    assert isinstance(data["devices"], dict)
    for key, value in data["devices"].items():
        assert value in [True, False]


def test_get_data_with_sensor_error(
    client, mock_temperature_sensor, mock_serial_devices
):
    """Test get_data endpoint when sensors fail."""
    # mock_temperature_sensor.side_effect = Exception("Sensor error")
    with patch("chronos.app.mock_sensors", side_effect=Exception("Sensor error")):
        response = client.get("/get_data")

        assert response.status_code == 200

        data = response.json()
        print("data", data)
        assert isinstance(data["sensors"], dict)
        assert isinstance(data["sensors"], dict)
        assert data["status"] is False
        assert isinstance(data["devices"], dict)


def test_get_device_state(client, mock_serial_devices):
    """Test getting device state."""
    response = client.get("/device_state?device=0")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "state" in data
    assert data["id"] == 0
    assert isinstance(data["state"], bool)


def test_update_device_state(client, mock_serial_devices):
    """Test updating device state."""
    # Save original state
    original_state = mock_serial_devices[0].state

    try:
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 0
        assert data["state"] is True
        mock_serial_devices[0].state = True
    finally:
        # Restore original state
        mock_serial_devices[0].state = original_state


def test_get_device_state_invalid_id(client):
    """Test getting device state with invalid device ID."""
    response = client.get("/device_state?device=10")  # Invalid device ID
    assert response.status_code == 422  # Validation error


def test_update_device_state_invalid_id(client):
    """Test updating device state with invalid device ID."""
    response = client.post("/device_state", json={"id": 10, "state": True})
    assert response.status_code == 422  # Validation error


# Boiler endpoint tests with mocking
def test_get_boiler_stats_mock(client, mock_modbus_device):
    """Test getting boiler stats with mocked device."""
    mock_modbus_device.read_boiler_data.return_value = {
        "system_supply_temp": 154.4,
        "outlet_temp": 158.0,
        "inlet_temp": 149.0,
        "flue_temp": 176.0,
        "cascade_current_power": 50.0,
        "lead_firing_rate": 75.0,
        "pump_status": True,
        "flame_status": True,
    }

    response = client.get("/boiler_stats")
    assert response.status_code == 200
    data = response.json()
    assert data["system_supply_temp"] == 154.4
    assert data["outlet_temp"] == 158.0
    assert data["pump_status"] is True


def test_get_boiler_stats_error(client, mock_modbus_device):
    """Test error handling when getting boiler stats."""
    mock_modbus_device.read_boiler_data.side_effect = ModbusException(
        "Connection failed"
    )
    with patch(
        "chronos.app.mock_boiler_stats",
        side_effect=ModbusException("Connection failed"),
    ):
        response = client.get("/boiler_stats")
        assert response.status_code == 500
        assert "Connection failed" in response.json()["detail"]


def test_set_boiler_setpoint_mock(client, mock_modbus_device):
    """Test setting boiler setpoint with mocked device."""
    # Save original setpoint from operating status
    original_setpoint = mock_modbus_device.read_operating_status()["current_setpoint"]

    try:
        mock_modbus_device.set_boiler_setpoint.return_value = True
        response = client.post("/boiler_set_setpoint", json={"temperature": 90.0})
        assert response.status_code == 200
        assert "90.0°F" in response.json()["message"]

        # Test rate limiting
        response = client.post("/boiler_set_setpoint", json={"temperature": 85.0})
        assert response.status_code == 429  # Too Many Requests
        assert "Too many temperature changes" in response.json()["detail"]
    finally:
        # Restore original setpoint
        mock_modbus_device.set_boiler_setpoint.return_value = True
        mock_modbus_device.set_boiler_setpoint(original_setpoint)


def test_set_boiler_setpoint_validation(client):
    """Test setpoint temperature validation."""
    # Test temperature too low
    response = client.post("/boiler_set_setpoint", json={"temperature": 69.9})
    assert response.status_code == 422

    # Test temperature too high
    response = client.post("/boiler_set_setpoint", json={"temperature": 110.1})
    assert response.status_code == 422


def test_get_boiler_operating_status_mock(client, mock_modbus_device):
    """Test getting boiler operating status with mocked device."""
    mock_modbus_device.read_operating_status.return_value = {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 158.0,
    }

    response = client.get("/boiler_status")
    assert response.status_code == 200
    data = response.json()
    assert data["operating_mode"] == 3
    assert data["operating_mode_str"] == "Central Heat"
    assert data["current_setpoint"] == 158.0


def test_set_boiler_setpoint_failure(client, mock_modbus_device):
    """Test failure when setting boiler setpoint."""
    mock_modbus_device.set_boiler_setpoint.return_value = False
    response = client.post("/boiler_set_setpoint", json={"temperature": 90.0})
    assert response.status_code == 500
    assert "Failed to set temperature" in response.json()["detail"]


def test_set_boiler_setpoint_connection_error(client, mock_modbus_device):
    """Test connection error when setting boiler setpoint."""
    mock_modbus_device.set_boiler_setpoint.side_effect = ModbusException(
        "Connection failed"
    )
    response = client.post("/boiler_set_setpoint", json={"temperature": 90.0})
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]


def test_download_log_success(client, mock_log_file):
    """Test successful log file download."""
    response = client.get("/download_log")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "Test log content" in response.text


def test_download_log_file_not_found(client, mock_log_file):
    """Test log file download when file doesn't exist."""
    # Remove the log file
    os.unlink(mock_log_file)

    response = client.get("/download_log")
    assert response.status_code == 500
    assert "Failed to read log file" in response.json()["detail"]
    assert "does not exist" in response.json()["detail"]


# Hardware tests (skipped by default)
@pytest.mark.skipif(not is_modbus_connected(), reason="No modbus connection available")
def test_get_boiler_stats_hardware(client):
    """Test getting boiler stats with real hardware."""
    response = client.get("/boiler_stats")
    assert response.status_code == 200
    data = response.json()
    # Basic validation of returned data structure
    assert "system_supply_temp" in data
    assert "outlet_temp" in data
    assert "inlet_temp" in data
    assert isinstance(data["pump_status"], bool)
    assert isinstance(data["flame_status"], bool)


@pytest.mark.skipif(not is_modbus_connected(), reason="No modbus connection available")
def test_set_boiler_setpoint_hardware(client):
    """Test setting boiler setpoint with real hardware."""
    # Get original setpoint
    status_response = client.get("/boiler_status")
    assert status_response.status_code == 200
    original_setpoint = status_response.json()["current_setpoint"]

    try:
        test_temp = 90.0
        response = client.post("/boiler_set_setpoint", json={"temperature": test_temp})
        assert response.status_code == 200

        # Verify the setpoint was actually set
        status_response = client.get("/boiler_status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert (
            abs(status_data["current_setpoint"] - test_temp) < 2.0
        )  # Allow small difference due to conversion
    finally:
        # Restore original setpoint
        restore_response = client.post(
            "/boiler_set_setpoint", json={"temperature": original_setpoint}
        )
        assert restore_response.status_code == 200

        # Verify restoration
        final_status = client.get("/boiler_status")
        assert final_status.status_code == 200
        assert abs(final_status.json()["current_setpoint"] - original_setpoint) < 2.0


# Test error cases with real hardware (if available)
@pytest.mark.skipif(not is_modbus_connected(), reason="No modbus connection available")
def test_invalid_setpoint_range_hardware(client):
    """Test setting invalid setpoint ranges with real hardware."""
    # Test minimum boundary
    response = client.post("/boiler_set_setpoint", json={"temperature": 69.9})
    assert response.status_code == 422

    # Test maximum boundary
    response = client.post("/boiler_set_setpoint", json={"temperature": 110.1})
    assert response.status_code == 422

    # Test valid boundary conditions
    response = client.post("/boiler_set_setpoint", json={"temperature": 70.0})
    assert response.status_code == 200
    response = client.post("/boiler_set_setpoint", json={"temperature": 110.0})
    assert response.status_code == 200


@pytest.mark.parametrize("temperature,description", VALID_SETPOINTS)
def test_valid_setpoint_ranges(client, mock_modbus_device, temperature, description):
    """Test various valid setpoint temperatures."""
    original_setpoint = mock_modbus_device.read_operating_status()["current_setpoint"]

    try:
        mock_modbus_device.set_boiler_setpoint.return_value = True
        response = client.post(
            "/boiler_set_setpoint", json={"temperature": temperature}
        )
        assert response.status_code == 200
        assert f"{temperature}°F" in response.json()["message"]
    finally:
        mock_modbus_device.set_boiler_setpoint(original_setpoint)


@pytest.mark.parametrize("temperature,description", INVALID_SETPOINTS)
def test_invalid_setpoint_ranges(client, temperature, description):
    """Test various invalid setpoint temperatures."""
    response = client.post("/boiler_set_setpoint", json={"temperature": temperature})
    assert response.status_code == 422


@pytest.mark.parametrize("error,status_code,error_message", ERROR_SCENARIOS)
def test_error_handling_scenarios(
    client, mock_modbus_device, error, status_code, error_message
):
    """Test various error scenarios."""
    mock_modbus_device.read_boiler_data.side_effect = error

    # First call should return the original error
    with patch("chronos.app.mock_boiler_stats", side_effect=error):
        response = client.get("/boiler_stats")
        assert response.status_code == status_code
        assert error_message in response.json()["detail"]

    # After multiple failures, circuit breaker should open
    for _ in range(4):  # Already had one failure
        response = client.get("/boiler_stats")

    # Circuit breaker should be open now
    with patch("chronos.app.circuit_breaker.can_execute", return_value=False):
        response = client.get("/boiler_stats")
        assert response.status_code == 503  # Service Unavailable
        assert "Service temporarily unavailable" in response.json()["detail"]


@pytest.mark.integration
def test_complete_boiler_flow(client, mock_modbus_device):
    """Test the complete flow of boiler operations."""
    # 1. Get initial stats
    response = client.get("/boiler_stats")
    assert response.status_code == 200
    assert response.json()  # Verify we get valid JSON response

    # 2. Get current operating status
    response = client.get("/boiler_status")
    assert response.status_code == 200
    initial_status = response.json()

    # 3. Change setpoint
    original_setpoint = initial_status["current_setpoint"]
    try:
        new_temp = 90.0
        # Update mock device's operating status to reflect the new setpoint
        mock_modbus_device.read_operating_status.return_value = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": new_temp,
        }

        response = client.post("/boiler_set_setpoint", json={"temperature": new_temp})
        assert response.status_code == 200

        # Test rate limiting
        response = client.post("/boiler_set_setpoint", json={"temperature": 85.0})
        assert response.status_code == 429  # Too Many Requests

        # Wait for rate limit to expire (handled by reset_limiters fixture)

        # 4. Verify status changed
        response = client.get("/boiler_status")
        assert response.status_code == 200
        new_status = response.json()
        assert abs(new_status["current_setpoint"] - new_temp) < 2.0
    finally:
        # Update mock device's operating status back to original setpoint
        mock_modbus_device.read_operating_status.return_value = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": original_setpoint,
        }
        # Restore original setpoint
        client.post("/boiler_set_setpoint", json={"temperature": original_setpoint})


def test_get_temperature_limits_mock(client, mock_modbus_device):
    """Test getting temperature limits with mocked device."""
    mock_modbus_device.get_temperature_limits.return_value = {
        "min_setpoint": 75.0,
        "max_setpoint": 105.0,
    }
    response = client.get("/temperature_limits")
    assert response.status_code == 200
    data = response.json()
    assert "hard_limits" in data
    assert "soft_limits" in data
    assert data["soft_limits"]["min_setpoint"] == 75.0
    assert data["soft_limits"]["max_setpoint"] == 105.0


def test_set_temperature_limits_mock(client, mock_modbus_device):
    """Test setting temperature limits with mocked device."""
    mock_modbus_device.set_temperature_limits.return_value = True
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 75.0, "max_setpoint": 105.0}
    )
    assert response.status_code == 200
    assert "Temperature limits updated successfully" in response.json()["message"]


def test_set_temperature_limits_validation(client):
    """Test temperature limits validation."""
    # Test min > max
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 85.0, "max_setpoint": 75.0}
    )
    assert response.status_code == 422

    # Test outside hardware limits
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 65.0, "max_setpoint": 115.0}
    )
    assert response.status_code == 422


def test_set_temperature_limits_failure(client, mock_modbus_device):
    """Test failure when setting temperature limits."""
    mock_modbus_device.set_temperature_limits.return_value = False
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 75.0, "max_setpoint": 105.0}
    )
    assert response.status_code == 500
    assert "Failed to set temperature limits" in response.json()["detail"]


def test_set_temperature_limits_connection_error(client, mock_modbus_device):
    """Test connection error when setting temperature limits."""
    mock_modbus_device.set_temperature_limits.side_effect = ModbusException(
        "Connection failed"
    )
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 75.0, "max_setpoint": 105.0}
    )
    assert response.status_code == 503
    assert "Connection failed" in response.json()["detail"]


def test_set_boiler_setpoint_read_only(client, mock_modbus_device):
    """Test that setting boiler setpoint is blocked in read-only mode."""
    # Enable read-only mode
    cfg.READ_ONLY_MODE = True
    try:
        response = client.post("/boiler_set_setpoint", json={"temperature": 90.0})
        assert response.status_code == 403
        assert (
            "Operation not permitted: system is in read-only mode"
            in response.json()["detail"]
        )
    finally:
        # Reset read-only mode to its original state
        cfg.READ_ONLY_MODE = False


def test_set_temperature_limits_read_only(client, mock_modbus_device):
    """Test that setting temperature limits is blocked in read-only mode."""
    # Enable read-only mode
    cfg.READ_ONLY_MODE = True
    try:
        # Test setting temperature limits
        response = client.post(
            "/temperature_limits", json={"min_setpoint": 75.0, "max_setpoint": 105.0}
        )
        assert response.status_code == 403
        assert (
            "Operation not permitted: system is in read-only mode"
            in response.json()["detail"]
        )

        # Verify that read operations still work
        response = client.get("/temperature_limits")
        assert response.status_code == 200
        data = response.json()
        assert "hard_limits" in data
        assert "soft_limits" in data
    finally:
        # Reset read-only mode to its original state
        cfg.READ_ONLY_MODE = False
