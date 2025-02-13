import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from chronos.app import app, circuit_breaker, rate_limiter
from chronos.config import cfg
from chronos.devices import ModbusDevice, SerialDevice
from fastapi.testclient import TestClient

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Test categories
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "mock: mark test as using mock devices")
    config.addinivalue_line("markers", "hardware: mark test as using real hardware")
    config.addinivalue_line("markers", "api: mark test as testing API endpoints")
    config.addinivalue_line("markers", "integration: mark test as integration test")


# Reset rate limiter and circuit breaker between tests
@pytest.fixture(autouse=True)
def reset_limiters():
    """Reset rate limiter and circuit breaker between tests."""
    rate_limiter.last_change_time = 0
    circuit_breaker.failure_count = 0
    circuit_breaker.is_open = False
    circuit_breaker.last_failure_time = 0


# State verification fixture
@pytest.fixture(autouse=True)
def verify_boiler_state():
    """Verify boiler state before and after each test."""
    if not has_modbus_connection():
        yield
        return

    # Get initial state
    with ModbusDevice(port=cfg.modbus.portname) as device:
        initial_state = {
            "setpoint": device.read_operating_status()["current_setpoint"],
            "mode": device.read_operating_status()["operating_mode"],
        }

    yield  # Run the test

    # Verify final state matches initial state
    with ModbusDevice(port=cfg.modbus.portname) as device:
        final_state = {
            "setpoint": device.read_operating_status()["current_setpoint"],
            "mode": device.read_operating_status()["operating_mode"],
        }

        # If states don't match, log warning and restore original state
        if final_state != initial_state:
            logger.warning(
                "Boiler state changed during test. "
                f"Initial: {initial_state}, Final: {final_state}. "
                "Restoring original state..."
            )
            device.set_boiler_setpoint(initial_state["setpoint"])


# Timeout decorator for hardware operations
def with_timeout(timeout_sec=5):
    """Decorator to add timeout to hardware operations."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal

            def handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {timeout_sec} seconds")

            # Set the timeout handler
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_sec)

            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Disable the alarm
                return result
            except TimeoutError:
                signal.alarm(0)  # Disable the alarm
                raise

        return wrapper

    return decorator


def has_modbus_connection():
    """Check if we can connect to the real modbus device."""
    try:
        with ModbusDevice(port=cfg.modbus.portname) as device:
            return device.is_connected()
    except Exception as e:
        logger.error(f"Error connecting to modbus device: {e}")
        return False


# FastAPI test client fixture
@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


# ModbusDevice fixtures
@pytest.fixture
def mock_modbus_client():
    """Fixture to provide a mocked ModbusSerialClient."""
    with patch("chronos.devices.ModbusSerialClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        # Default to successful connection
        mock_instance.connect.return_value = True
        mock_instance.is_socket_open.return_value = True
        yield mock_class  # Return the class mock, not the instance


@pytest.fixture
def device(mock_modbus_client):
    """Fixture to provide a ModbusDevice instance with mocked client."""
    device = ModbusDevice(port="/dev/ttyUSB0", baudrate=9600, parity="E")
    yield device
    device.close()


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
        "flame_status": True,
    }

    mock_device.read_operating_status.return_value = {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 158.0,
        "status": True,
        "setpoint_temperature": 158.0,
        "current_temperature": 155.5,
        "pressure": 15.2,
        "error_code": 0,
    }

    mock_device.read_model_info.return_value = {
        "model_id": 1,
        "model_name": "FTXL 85",
        "firmware_version": "1.2",
        "hardware_version": "3.4",
    }

    mock_device.read_error_history.return_value = {
        "last_lockout_code": 3,
        "last_lockout_str": "Low Water",
        "last_blockout_code": 8,
        "last_blockout_str": "Sensor Failure",
    }

    mock_device.set_boiler_setpoint.return_value = True

    # Mock the context manager
    with (
        patch("chronos.devices.ModbusDevice") as mock_device_class,
        patch("chronos.devices.create_modbus_connection") as mock_create,
    ):
        # Configure ModbusDevice mock
        mock_device_class.return_value = mock_device

        # Configure the context manager mock
        mock_create.return_value.__enter__.return_value = mock_device
        mock_create.return_value.__exit__.return_value = None

        yield mock_device


# SerialDevice fixtures
@pytest.fixture
def mock_serial_devices():
    """Mock all serial devices."""
    with patch("chronos.devices.SerialDevice") as mock:
        mock_instances = [MagicMock() for _ in range(5)]
        mock.side_effect = mock_instances
        for inst in mock_instances:
            inst.state = False
        yield mock_instances


@pytest.fixture
def device_serial():
    """Create a SerialDevice instance for testing."""
    return SerialDevice(id=0, portname=cfg.serial.portname, baudrate=19200)


# Temperature sensor fixture
@pytest.fixture
def mock_temperature_sensor():
    """Mock temperature sensor readings."""
    with patch("chronos.devices.read_temperature_sensor") as mock:
        mock.return_value = 72.5  # Default test temperature in °F
        yield mock


# Log file fixture
@pytest.fixture
def mock_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Test log content\n")
        temp_path = f.name

    # Mock the config to use our temporary file
    original_path = cfg.files.log_path
    cfg.files.log_path = temp_path

    yield temp_path

    # Cleanup
    cfg.files.log_path = original_path
    try:
        os.unlink(temp_path)
    except OSError:
        pass
