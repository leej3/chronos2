from unittest.mock import MagicMock, patch

import pytest
from chronos.devices import ModbusDevice, ModbusException
from pymodbus.exceptions import ModbusIOException


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


@pytest.fixture
def mock_modbus_device():
    """Create a mock ModbusDevice with mocked client."""
    with patch("chronos.devices.ModbusSerialClient") as mock_client, patch(
        "chronos.devices.cfg"
    ) as mock_cfg:
        # Mock successful connection
        mock_client.return_value.connect.return_value = True
        mock_client.return_value.is_socket_open.return_value = True

        # Create struct-like objects for registers
        class Registers:
            def __init__(self):
                self.holding = type(
                    "Holding",
                    (),
                    {
                        "operating_mode": 0x40000,
                        "cascade_mode": 0x40001,
                        "setpoint": 0x40002,
                        "min_setpoint": 0x40003,
                        "max_setpoint": 0x40004,
                        "system_supply_temp": 0x40006,
                    },
                )()
                self.input = type(
                    "Input",
                    (),
                    {
                        "alarm": 0x30003,
                        "pump": 0x30004,
                        "flame": 0x30005,
                        "cascade_current_power": 0x30006,
                        "outlet_temp": 0x30008,
                        "inlet_temp": 0x30009,
                        "flue_temp": 0x30010,
                        "lead_firing_rate": 0x30011,
                    },
                )()

        # Mock the config
        mock_cfg.modbus.registers = Registers()
        mock_cfg.modbus.operating_modes = {
            "0": "Initialization",
            "1": "Standby",
            "2": "CH",
            "3": "DHW",
            "4": "Manual",
        }
        mock_cfg.modbus.cascade_modes = {
            "0": "Single Boiler",
            "1": "Leader",
            "2": "Member",
        }
        mock_cfg.modbus.error_codes = {
            "0": "No Error",
            "1": "Ignition Failure",
            "2": "Flame Failure",
            "3": "Low Water",
        }
        mock_cfg.modbus.model_ids = {"1": "NeoTherm", "2": "FTX", "3": "XFyre"}

        device = ModbusDevice()
        yield device


def test_modbus_device_connection(mock_modbus_device):
    """Test basic connection functionality."""
    assert mock_modbus_device.is_connected() is True


@pytest.mark.parametrize(
    "registers,expected",
    [
        # Test case 1: Normal operation
        (
            {
                "holding": [
                    1,
                    2,
                    150,
                    120,
                    180,
                    0,
                    220,
                ],  # Mode, Cascade, Setpoints, Supply
                "input": [
                    1,
                    1,
                    1,
                    86,
                    0,
                    180,
                    160,
                    200,
                    66,
                ],  # Status, Power, Temps, Rate
            },
            {
                "operating_mode": 1,
                "operating_mode_str": "Standby",
                "cascade_mode": 2,
                "cascade_mode_str": "Member",
                "system_supply_temp": round((9.0 / 5.0) * (220 / 10.0) + 32.0, 1),
                "outlet_temp": round((9.0 / 5.0) * (180 / 10.0) + 32.0, 1),
                "inlet_temp": round((9.0 / 5.0) * (160 / 10.0) + 32.0, 1),
                "flue_temp": round((9.0 / 5.0) * (200 / 10.0) + 32.0, 1),
                "alarm_status": True,
                "pump_status": True,
                "flame_status": True,
                "cascade_current_power": 86.0,
                "lead_firing_rate": 66.0,
            },
        ),
        # Test case 2: All zeros/off
        (
            {"holding": [0, 0, 0, 0, 0, 0, 0], "input": [0, 0, 0, 0, 0, 0, 0, 0, 0]},
            {
                "operating_mode": 0,
                "operating_mode_str": "Initialization",
                "cascade_mode": 0,
                "cascade_mode_str": "Single Boiler",
                "system_supply_temp": 32.0,
                "outlet_temp": 32.0,
                "inlet_temp": 32.0,
                "flue_temp": 32.0,
                "alarm_status": False,
                "pump_status": False,
                "flame_status": False,
                "cascade_current_power": 0.0,
                "lead_firing_rate": 0.0,
            },
        ),
    ],
)
def test_read_boiler_data(mock_modbus_device, registers, expected):
    """Test reading boiler data with different register values."""
    # Mock the register read responses
    mock_modbus_device.client.read_holding_registers.return_value.registers = registers[
        "holding"
    ]
    mock_modbus_device.client.read_holding_registers.return_value.isError.return_value = (
        False
    )

    mock_modbus_device.client.read_input_registers.return_value.registers = registers[
        "input"
    ]
    mock_modbus_device.client.read_input_registers.return_value.isError.return_value = (
        False
    )

    # Read data
    result = mock_modbus_device.read_boiler_data()

    # Verify all expected values
    for key, value in expected.items():
        assert (
            result[key] == value
        ), f"Mismatch for {key}: expected {value}, got {result[key]}"


def test_read_boiler_data_disconnected(mock_modbus_device):
    """Test reading when device is disconnected."""
    mock_modbus_device.client.is_socket_open.return_value = False
    with pytest.raises(ModbusException, match="Device not connected"):
        mock_modbus_device.read_boiler_data()


def test_read_boiler_data_retry_success(mock_modbus_device):
    """Test successful retry after initial failure."""
    # First call fails, second succeeds
    mock_modbus_device.client.read_holding_registers.side_effect = [
        ModbusIOException("First attempt fails"),
        MagicMock(registers=[1, 2, 150, 120, 180, 0, 220], isError=lambda: False),
        MagicMock(
            registers=[1, 2, 150, 120, 180, 0, 220], isError=lambda: False
        ),  # Add extra for potential retries
    ]
    mock_modbus_device.client.read_input_registers.return_value = MagicMock(
        registers=[1, 1, 1, 86, 0, 180, 160, 200, 66], isError=lambda: False
    )

    result = mock_modbus_device.read_boiler_data()
    assert result is not None
    assert result["operating_mode"] == 1
    assert result["cascade_current_power"] == 86.0


def test_read_boiler_data_all_retries_fail(mock_modbus_device):
    """Test when all retry attempts fail."""
    mock_modbus_device.client.read_holding_registers.side_effect = ModbusIOException(
        "Communication failed"
    )

    result = mock_modbus_device.read_boiler_data(max_retries=3)
    assert result is None
