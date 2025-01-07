import os
import pytest
from chronos.devices import ModbusException
from chronos.devices import ModbusDevice
from chronos.config import cfg

# Test data for parametrized tests
VALID_SETPOINTS = [
    (120.0, "minimum valid temperature"),
    (150.0, "typical operating temperature"),
    (180.0, "maximum valid temperature")
]

INVALID_SETPOINTS = [
    (119.9, "below minimum"),
    (180.1, "above maximum"),
    (0.0, "zero temperature"),
    (-10.0, "negative temperature")
]

ERROR_SCENARIOS = [
    (ModbusException("Connection failed"), 500, "Connection failed"),
    (ModbusException("Timeout"), 500, "Timeout"),
    (ValueError("Invalid response"), 500, "Invalid response"),
    (RuntimeError("Unknown error"), 500, "Unknown error")
]

def has_modbus_connection():
    """Check if we can connect to the real modbus device."""
    try:
        with ModbusDevice(port=cfg.modbus.portname) as device:
            return device.is_connected()
    except:
        return False

# Legacy endpoint tests
def test_get_data(client, mock_temperature_sensor, mock_serial_devices):
    """Test the legacy get_data endpoint."""
    response = client.get("/get_data")
    assert response.status_code == 200
    data = response.json()
    assert "sensors" in data
    assert "devices" in data
    assert data["sensors"]["supply"] == 72.5
    assert data["sensors"]["return"] == 72.5
    assert data["sensors"]["outdoor"] is None

def test_get_data_with_sensor_error(client, mock_temperature_sensor, mock_serial_devices):
    """Test get_data endpoint when sensors fail."""
    mock_temperature_sensor.side_effect = Exception("Sensor error")
    response = client.get("/get_data")
    assert response.status_code == 200
    data = response.json()
    assert data["sensors"]["supply"] is None
    assert data["sensors"]["return"] is None
    assert data["sensors"]["outdoor"] is None
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
        "water_flow_rate": 10.0,
        "pump_status": True,
        "flame_status": True
    }

    response = client.get("/boiler_stats")
    assert response.status_code == 200
    data = response.json()
    assert data["system_supply_temp"] == 154.4
    assert data["outlet_temp"] == 158.0
    assert data["pump_status"] is True

def test_get_boiler_stats_error(client, mock_modbus_device):
    """Test error handling when getting boiler stats."""
    mock_modbus_device.read_boiler_data.side_effect = ModbusException("Connection failed")

    response = client.get("/boiler_stats")
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]

def test_set_boiler_setpoint_mock(client, mock_modbus_device):
    """Test setting boiler setpoint with mocked device."""
    # Save original setpoint from operating status
    original_setpoint = mock_modbus_device.read_operating_status()["current_setpoint"]
    
    try:
        mock_modbus_device.set_boiler_setpoint.return_value = True
        response = client.post("/boiler_set_setpoint", json={"temperature": 140.0})
        assert response.status_code == 200
        assert "140.0°F" in response.json()["message"]
        
        # Test rate limiting
        response = client.post("/boiler/set_setpoint", json={"temperature": 150.0})
        assert response.status_code == 429  # Too Many Requests
        assert "Too many temperature changes" in response.json()["detail"]
    finally:
        # Restore original setpoint
        mock_modbus_device.set_boiler_setpoint.return_value = True
        mock_modbus_device.set_boiler_setpoint(original_setpoint)

def test_set_boiler_setpoint_validation(client):
    """Test setpoint temperature validation."""
    # Test temperature too low
    response = client.post("/boiler_set_setpoint", json={"temperature": 110.0})
    assert response.status_code == 422

    # Test temperature too high
    response = client.post("/boiler_set_setpoint", json={"temperature": 190.0})
    assert response.status_code == 422

def test_get_boiler_operating_status_mock(client, mock_modbus_device):
    """Test getting boiler operating status with mocked device."""
    mock_modbus_device.read_operating_status.return_value = {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 158.0
    }

    response = client.get("/boiler_status")
    assert response.status_code == 200
    data = response.json()
    assert data["operating_mode"] == 3
    assert data["operating_mode_str"] == "Central Heat"
    assert data["current_setpoint"] == 158.0

def test_get_boiler_model_info_mock(client, mock_modbus_device):
    """Test getting boiler model information with mocked device."""
    mock_modbus_device.read_model_info.return_value = {
        "model_id": 1,
        "model_name": "FTXL 85",
        "firmware_version": "1.2",
        "hardware_version": "3.4"
    }

    response = client.get("/boiler_info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == 1
    assert data["model_name"] == "FTXL 85"
    assert data["firmware_version"] == "1.2"
    assert data["hardware_version"] == "3.4"

def test_get_boiler_model_info_error(client, mock_modbus_device):
    """Test error handling when getting boiler model info."""
    mock_modbus_device.read_model_info.return_value = {}

    response = client.get("/boiler_info")
    assert response.status_code == 500
    assert "Failed to read model info" in response.json()["detail"]

def test_get_boiler_error_history_mock(client, mock_modbus_device):
    """Test getting boiler error history with mocked device."""
    mock_modbus_device.read_error_history.return_value = {
        "last_lockout_code": 3,
        "last_lockout_str": "Low Water",
        "last_blockout_code": 8,
        "last_blockout_str": "Sensor Failure"
    }

    response = client.get("/boiler_errors")
    assert response.status_code == 200
    data = response.json()
    assert data["last_lockout_code"] == 3
    assert "Low Water" in data["last_lockout_str"]
    assert data["last_blockout_code"] == 8
    assert "Sensor Failure" in data["last_blockout_str"]

def test_get_boiler_error_history_no_errors(client, mock_modbus_device):
    """Test getting boiler error history when no errors exist."""
    mock_modbus_device.read_error_history.return_value = {}

    response = client.get("/boiler/errors")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "last_lockout_code": None,
        "last_lockout_str": None,
        "last_blockout_code": None,
        "last_blockout_str": None
    }

def test_set_boiler_setpoint_failure(client, mock_modbus_device):
    """Test failure when setting boiler setpoint."""
    mock_modbus_device.set_boiler_setpoint.return_value = False
    
    response = client.post("/boiler_set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 500
    assert "Failed to set temperature" in response.json()["detail"]

def test_set_boiler_setpoint_connection_error(client, mock_modbus_device):
    """Test connection error when setting boiler setpoint."""
    mock_modbus_device.set_boiler_setpoint.side_effect = ModbusException("Connection failed")
    
    response = client.post("/boiler_set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]
    
    # Test circuit breaker after multiple failures
    for _ in range(5):
        response = client.post("/boiler_set_setpoint", json={"temperature": 140.0})
    
    # Circuit breaker should be open now
    response = client.post("/boiler/set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 503  # Service Unavailable
    assert "Service temporarily unavailable" in response.json()["detail"]

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
@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
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

@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_set_boiler_setpoint_hardware(client):
    """Test setting boiler setpoint with real hardware."""
    # Get original setpoint
    status_response = client.get("/boiler_status")
    assert status_response.status_code == 200
    original_setpoint = status_response.json()["current_setpoint"]

    try:
        test_temp = 140.0
        response = client.post("/boiler_set_setpoint", json={"temperature": test_temp})
        assert response.status_code == 200

        # Verify the setpoint was actually set
        status_response = client.get("/boiler_status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert abs(status_data["current_setpoint"] - test_temp) < 2.0  # Allow small difference due to conversion
    finally:
        # Restore original setpoint
        restore_response = client.post("/boiler_set_setpoint", json={"temperature": original_setpoint})
        assert restore_response.status_code == 200

        # Verify restoration
        final_status = client.get("/boiler_status")
        assert final_status.status_code == 200
        assert abs(final_status.json()["current_setpoint"] - original_setpoint) < 2.0

@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_get_boiler_error_history_hardware(client):
    """Test getting error history with real hardware."""
    response = client.get("/boiler_errors")
    assert response.status_code == 200
    data = response.json()
    # Verify the structure of the response
    if "last_lockout_code" in data:
        assert "last_lockout_str" in data
    if "last_blockout_code" in data:
        assert "last_blockout_str" in data

@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_get_boiler_model_info_hardware(client):
    """Test getting model info with real hardware."""
    response = client.get("/boiler_info")
    assert response.status_code == 200
    data = response.json()
    # Verify the structure and basic validation of the response
    assert "model_id" in data
    assert "model_name" in data
    assert "firmware_version" in data
    assert "hardware_version" in data
    # Model ID should be a positive integer
    assert isinstance(data["model_id"], int)
    assert data["model_id"] > 0
    # Version strings should follow x.y format
    assert all(len(v.split(".")) == 2 for v in [data["firmware_version"], data["hardware_version"]])

# Test error cases with real hardware (if available)
@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_invalid_setpoint_range_hardware(client):
    """Test setting invalid setpoint ranges with real hardware."""
    # Test minimum boundary
    response = client.post("/boiler_set_setpoint", json={"temperature": 119.9})
    assert response.status_code == 422

    # Test maximum boundary
    response = client.post("/boiler_set_setpoint", json={"temperature": 180.1})
    assert response.status_code == 422

    # Test valid boundary conditions
    response = client.post("/boiler_set_setpoint", json={"temperature": 120.0})
    assert response.status_code == 200
    response = client.post("/boiler_set_setpoint", json={"temperature": 180.0})
    assert response.status_code == 200

@pytest.mark.parametrize("temperature,description", VALID_SETPOINTS)
def test_valid_setpoint_ranges(client, mock_modbus_device, temperature, description):
    """Test various valid setpoint temperatures."""
    original_setpoint = mock_modbus_device.read_operating_status()["current_setpoint"]
    
    try:
        mock_modbus_device.set_boiler_setpoint.return_value = True
        response = client.post("/boiler_set_setpoint", json={"temperature": temperature})
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
def test_error_handling_scenarios(client, mock_modbus_device, error, status_code, error_message):
    """Test various error scenarios."""
    mock_modbus_device.read_boiler_data.side_effect = error
    
    # First call should return the original error
    response = client.get("/boiler_stats")
    assert response.status_code == status_code
    assert error_message in response.json()["detail"]
    
    # After multiple failures, circuit breaker should open
    for _ in range(4):  # Already had one failure
        response = client.get("/boiler_stats")
    
    # Circuit breaker should be open now
    response = client.get("/boiler_stats")
    assert response.status_code == 503  # Service Unavailable
    assert "Service temporarily unavailable" in response.json()["detail"]

@pytest.mark.integration
def test_complete_boiler_flow(client, mock_modbus_device):
    """Test the complete flow of boiler operations."""
    # 1. Get initial stats
    response = client.get("/boiler_stats")
    assert response.status_code == 200
    initial_stats = response.json()
    
    # 2. Get current operating status
    response = client.get("/boiler_status")
    assert response.status_code == 200
    initial_status = response.json()
    
    # 3. Change setpoint
    original_setpoint = initial_status["current_setpoint"]
    try:
        new_temp = 140.0
        # Update mock device's operating status to reflect the new setpoint
        mock_modbus_device.read_operating_status.return_value = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": new_temp
        }
        
        response = client.post("/boiler_set_setpoint", json={"temperature": new_temp})
        assert response.status_code == 200
        
        # Test rate limiting
        response = client.post("/boiler_set_setpoint", json={"temperature": 150.0})
        assert response.status_code == 429  # Too Many Requests
        
        # Wait for rate limit to expire (handled by reset_limiters fixture)
        
        # 4. Verify status changed
        response = client.get("/boiler_status")
        assert response.status_code == 200
        new_status = response.json()
        assert abs(new_status["current_setpoint"] - new_temp) < 2.0
        
        # 5. Get model info
        response = client.get("/boiler_info")
        assert response.status_code == 200
        model_info = response.json()
        assert model_info["model_id"] > 0
        
        # 6. Check error history
        response = client.get("/boiler_errors")
        assert response.status_code == 200
    finally:
        # Update mock device's operating status back to original setpoint
        mock_modbus_device.read_operating_status.return_value = {
            "operating_mode": 3,
            "operating_mode_str": "Central Heat",
            "cascade_mode": 0,
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": original_setpoint
        }
        # Restore original setpoint
        client.post("/boiler_set_setpoint", json={"temperature": original_setpoint})