from unittest.mock import patch, MagicMock


def test_initial_state_is_none_before_reading(device_serial):
    # Check internal state is initially None
    assert device_serial._state is None
    # This triggers a read from the mock device (if mocked)
    _ = device_serial.state
    # If _send_command is still not mocked, no real hardware call should happen
    # unless you actually have a device plugged in.


@patch("chronos.devices.Serial")
def test_read_state_from_device_on(mock_serial, device_serial):
    """
    Mock the serial response to simulate a device that's turned 'on'.
    """
    mock_port = MagicMock()
    mock_port.readall.return_value = b"relay read 0 \n\n\ron\n\r>"
    mock_serial.return_value.__enter__.return_value = mock_port

    current_state = device_serial.read_state_from_device()
    assert current_state is True
    assert device_serial._state is True


@patch("chronos.devices.Serial")
def test_read_state_from_device_off(mock_serial, device_serial):
    """
    Mock the serial response to simulate a device that's turned 'off'.
    """
    mock_port = MagicMock()
    mock_port.readall.return_value = b"relay read 0 \n\n\roff\n\r>"
    mock_serial.return_value.__enter__.return_value = mock_port

    current_state = device_serial.read_state_from_device()
    assert current_state is False
    assert device_serial._state is False


@patch("chronos.devices.Serial")
def test_set_state_to_on(mock_serial, device_serial):
    """
    Test setting the device state to 'on'. We mock the serial so no real hardware is needed.
    """
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port

    device_serial.state = True
    assert device_serial._state is True
    mock_port.write.assert_any_call(b"relay on 0\n\r")


@patch("chronos.devices.Serial")
def test_set_state_to_off(mock_serial, device_serial):
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port

    device_serial.state = False
    assert device_serial._state is False
    mock_port.write.assert_any_call(b"relay off 0\n\r")


@patch("chronos.devices.Serial", side_effect=Exception("Serial not accessible"))
def test_send_command_exception(mock_serial, device_serial, caplog):
    """
    Test behavior when the serial connection is absent/unusable (e.g., cable unplugged).
    The code should gracefully handle the exception, log a warning, and return an "off" response
    that includes the correct device ID.
    """
    # This should trigger the exception and fallback to mock response for device 0
    response0 = device_serial._send_command("relay read 0\n\r")
    # This should trigger the exception and fallback for device 1
    response1 = device_serial._send_command("relay read 1\n\r")

    # Check that each response includes relay read <device_id> and "off"
    assert "relay read 0" in response0
    assert "off" in response0
    assert "relay read 1" in response1
    assert "off" in response1

    # Confirm that a WARNING was logged about the serial port not being accessible
    # (caplog.messages is a list of the captured log messages)
    warning_messages = [
        record.message for record in caplog.records if record.levelname == "WARNING"
    ]
    assert any("Serial port not accessible" in msg for msg in warning_messages)
    assert any(
        "Returning mock response for debugging" in msg for msg in warning_messages
    )
