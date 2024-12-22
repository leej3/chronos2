import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from chronos.devices import ModbusDevice, ModbusException
from chronos.app import app, DEVICES, DeviceTuple, SerialDevice

# Constants for testing
TEST_SERIAL_PORT = "/dev/ttyACM0"
TEST_MODBUS_PORT = "/dev/ttyUSB0"

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_modbus_device():
    """Mock ModbusDevice for testing."""
    mock_device = MagicMock()
    mock_device.is_connected.return_value = True
    
    # Set default return values for commonly used methods
    mock_device.read_boiler_data.return_value = {
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
    
    mock_device.read_operating_status.return_value = {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 158.0
    }
    
    mock_device.read_model_info.return_value = {
        "model_id": 1,
        "model_name": "FTXL 85",
        "firmware_version": "1.2",
        "hardware_version": "3.4"
    }
    
    mock_device.read_error_history.return_value = {
        "last_lockout_code": 3,
        "last_lockout_str": "Low Water",
        "last_blockout_code": 8,
        "last_blockout_str": "Sensor Failure"
    }
    
    mock_device.set_boiler_setpoint.return_value = True
    
    # Mock the context manager
    with patch('chronos.devices.ModbusDevice') as mock_device_class, \
         patch('chronos.devices.create_modbus_connection') as mock_create:
        
        # Configure ModbusDevice mock
        mock_device_class.return_value = mock_device
        
        # Configure the context manager mock
        mock_create.return_value.__enter__.return_value = mock_device
        mock_create.return_value.__exit__.return_value = None
        
        yield mock_device

@pytest.fixture
def mock_serial_devices():
    """Mock all serial devices."""
    with patch('chronos.devices.SerialDevice') as mock:
        mock_instances = [MagicMock() for _ in range(5)]
        mock.side_effect = mock_instances
        for inst in mock_instances:
            inst.state = False
        yield mock_instances

@pytest.fixture
def mock_temperature_sensor():
    """Mock temperature sensor readings."""
    with patch('chronos.devices.read_temperature_sensor') as mock:
        mock.return_value = 72.5  # Default test temperature in °F
        yield mock

def has_modbus_connection():
    """Check if we can connect to the real modbus device."""
    try:
        with ModbusDevice(port=TEST_MODBUS_PORT) as device:
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
    response = client.post("/device_state", json={"id": 0, "state": True})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 0
    assert data["state"] is True
    mock_serial_devices[0].state = True

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
    
    response = client.get("/boiler/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["system_supply_temp"] == 154.4
    assert data["outlet_temp"] == 158.0
    assert data["pump_status"] is True

def test_get_boiler_stats_error(client, mock_modbus_device):
    """Test error handling when getting boiler stats."""
    mock_modbus_device.read_boiler_data.side_effect = ModbusException("Connection failed")
    
    response = client.get("/boiler/stats")
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]

def test_set_boiler_setpoint_mock(client, mock_modbus_device):
    """Test setting boiler setpoint with mocked device."""
    mock_modbus_device.set_boiler_setpoint.return_value = True
    
    response = client.post("/boiler/set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 200
    assert "140.0°F" in response.json()["message"]

def test_set_boiler_setpoint_validation(client):
    """Test setpoint temperature validation."""
    # Test temperature too low
    response = client.post("/boiler/set_setpoint", json={"temperature": 110.0})
    assert response.status_code == 422

    # Test temperature too high
    response = client.post("/boiler/set_setpoint", json={"temperature": 190.0})
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
    
    response = client.get("/boiler/status")
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
    
    response = client.get("/boiler/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == 1
    assert data["model_name"] == "FTXL 85"
    assert data["firmware_version"] == "1.2"
    assert data["hardware_version"] == "3.4"

def test_get_boiler_model_info_error(client, mock_modbus_device):
    """Test error handling when getting boiler model info."""
    mock_modbus_device.read_model_info.return_value = {}
    
    response = client.get("/boiler/info")
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
    
    response = client.get("/boiler/errors")
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
    
    response = client.post("/boiler/set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 500
    assert "Failed to set temperature" in response.json()["detail"]

def test_set_boiler_setpoint_connection_error(client, mock_modbus_device):
    """Test connection error when setting boiler setpoint."""
    mock_modbus_device.set_boiler_setpoint.side_effect = ModbusException("Connection failed")
    
    response = client.post("/boiler/set_setpoint", json={"temperature": 140.0})
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]

def test_download_log_not_implemented(client):
    """Test the not implemented download_log endpoint."""
    response = client.get("/download_log")
    assert response.status_code == 501  # Not Implemented

# Hardware tests (skipped by default)
@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_get_boiler_stats_hardware(client):
    """Test getting boiler stats with real hardware."""
    response = client.get("/boiler/stats")
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
    test_temp = 140.0
    response = client.post("/boiler/set_setpoint", json={"temperature": test_temp})
    assert response.status_code == 200
    
    # Verify the setpoint was actually set
    status_response = client.get("/boiler/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert abs(status_data["current_setpoint"] - test_temp) < 2.0  # Allow small difference due to conversion

@pytest.mark.skipif(not has_modbus_connection(), reason="No modbus connection available")
def test_get_boiler_error_history_hardware(client):
    """Test getting error history with real hardware."""
    response = client.get("/boiler/errors")
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
    response = client.get("/boiler/info")
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
    response = client.post("/boiler/set_setpoint", json={"temperature": 119.9})
    assert response.status_code == 422
    
    # Test maximum boundary
    response = client.post("/boiler/set_setpoint", json={"temperature": 180.1})
    assert response.status_code == 422
    
    # Test valid boundary conditions
    response = client.post("/boiler/set_setpoint", json={"temperature": 120.0})
    assert response.status_code == 200
    response = client.post("/boiler/set_setpoint", json={"temperature": 180.0})
    assert response.status_code == 200