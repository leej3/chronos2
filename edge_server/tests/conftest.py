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
    with patch("chronos.devices.hardware.ModbusDevice") as mock_class:
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
def mock_modbus_device(monkeypatch):
    """Mock ModbusDevice for testing."""
    mock_device = MagicMock(spec=ModbusDevice)
    mock_device.is_connected.return_value = True

    # Add mock client
    mock_client = MagicMock()
    mock_client.is_socket_open.return_value = True
    mock_device.client = mock_client

    mock_device.read_boiler_data.return_value = {
        "system_supply_temp": 154.4,
        "outlet_temp": 158.0,
        "inlet_temp": 149.0,
        "flue_temp": 176.0,
        "cascade_current_power": 50.0,
        "lead_firing_rate": 75.0,
        "pump_status": True,
        "flame_status": True,
    }
    mock_device.read_operating_status.return_value = {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 90.0,
    }
    mock_device.set_boiler_setpoint.return_value = True
    mock_device.get_temperature_limits.return_value = {
        "min_setpoint": 75.0,
        "max_setpoint": 105.0,
    }
    mock_device.set_temperature_limits.return_value = True

    # Create a context manager mock that returns our mock_device
    mock_context = MagicMock()
    mock_context.__enter__ = lambda _: mock_device
    mock_context.__exit__ = lambda *args: None

    # Patch the create_modbus_connection function to return our mock context
    monkeypatch.setattr(
        "chronos.devices.create_modbus_connection", lambda: mock_context
    )
    return mock_device


# SerialDevice fixtures
@pytest.fixture
def mock_serial_devices(monkeypatch):
    """Mock serial devices for testing."""
    mock_devices = []
    for i in range(5):
        device = MagicMock()
        device.id = i
        device.state = True
        mock_devices.append(device)

    monkeypatch.setattr("chronos.app.DEVICES", mock_devices)
    return mock_devices


@pytest.fixture
def device_serial():
    """Create a SerialDevice instance for testing."""
    return SerialDevice(id=0, portname=cfg.serial.portname, baudrate=19200)


# Temperature sensor fixture
@pytest.fixture
def mock_temperature_sensor(monkeypatch):
    """Mock temperature sensor for testing."""

    def mock_read_temp(*args, **kwargs):
        return 75.0

    monkeypatch.setattr("chronos.app.safe_read_temperature", mock_read_temp)


# Log file fixture
@pytest.fixture
def mock_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Test log content")
        temp_file.flush()
        cfg.files.log_path = temp_file.name
        yield temp_file.name
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before each test."""
    original_mock_devices = cfg.MOCK_DEVICES
    original_read_only = cfg.READ_ONLY_MODE
    yield
    cfg.MOCK_DEVICES = original_mock_devices
    cfg.READ_ONLY_MODE = original_read_only
