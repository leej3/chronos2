import pytest
from unittest.mock import patch, MagicMock
from chronos.lib.devices import SerialDevice
from chronos.lib.logging import root_logger as logger

@pytest.fixture
def device():
    # Create a Device instance for testing. The ID is arbitrary here.
    return SerialDevice(id=0, portname="/dev/ttyACM0", baudrate=19200)

def test_initial_state_is_none_before_reading(device):
    # Check internal state is initially None
    assert device._state is None  
    # This triggers a read from the mock device (if mocked)
    _ = device.state  
    # If _send_command is still not mocked, no real hardware call should happen
    # unless you actually have a device plugged in.

@patch("chronos.lib.devices.Serial")
def test_read_state_from_device_on(mock_serial, device):
    """
    Mock the serial response to simulate a device that's turned 'on'.
    """
    mock_port = MagicMock()
    mock_port.readall.return_value = b"relay read 0 \n\n\ron\n\r>"
    mock_serial.return_value.__enter__.return_value = mock_port
    
    current_state = device.read_state_from_device()
    assert current_state is True
    assert device._state is True

@patch("chronos.lib.devices.Serial")
def test_read_state_from_device_off(mock_serial, device):
    """
    Mock the serial response to simulate a device that's turned 'off'.
    """
    mock_port = MagicMock()
    mock_port.readall.return_value = b"relay read 0 \n\n\roff\n\r>"
    mock_serial.return_value.__enter__.return_value = mock_port
    
    current_state = device.read_state_from_device()
    assert current_state is False
    assert device._state is False

@patch("chronos.lib.devices.Serial")
def test_set_state_to_on(mock_serial, device):
    """
    Test setting the device state to 'on'. We mock the serial so no real hardware is needed.
    """
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port
    
    device.state = True
    assert device._state is True
    mock_port.write.assert_any_call(b"relay on 0\n\r")

@patch("chronos.lib.devices.Serial")
def test_set_state_to_off(mock_serial, device):
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port
    
    device.state = False
    assert device._state is False
    mock_port.write.assert_any_call(b"relay off 0\n\r")

@patch("chronos.lib.devices.Serial", side_effect=Exception("Serial not accessible"))
def test_send_command_exception(mock_serial, device, caplog):
    """
    Test behavior when the serial connection is absent/unusable (e.g., cable unplugged).
    The code should gracefully handle the exception, log a warning, and return an "off" response
    that includes the correct device ID.
    """
    # This should trigger the exception and fallback to mock response for device 0
    response0 = device._send_command("relay read 0\n\r")
    # This should trigger the exception and fallback for device 1
    response1 = device._send_command("relay read 1\n\r")

    # Check that each response includes relay read <device_id> and "off"
    assert "relay read 0" in response0
    assert "off" in response0
    assert "relay read 1" in response1
    assert "off" in response1

    # Confirm that a WARNING was logged about the serial port not being accessible
    # (caplog.messages is a list of the captured log messages)
    warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    assert any("Serial port not accessible" in msg for msg in warning_messages)
    assert any("Returning mock response for debugging" in msg for msg in warning_messages)
