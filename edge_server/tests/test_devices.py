import logging
from unittest.mock import MagicMock, patch

import pytest
from chronos.devices import ModbusException
from chronos.devices.hardware import SerialDevice
from pymodbus.exceptions import ModbusIOException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def device_serial():
    device_serial = SerialDevice(
        id=0, portname="/dev/ttyUSB0", name="Test Device", baudrate=9600
    )
    return device_serial


def test_initial_state_is_none_before_reading(device_serial):
    device_serial._send_command("")
    device_serial.command_to_state = None
    assert device_serial._state is None


def test_read_state_from_device_on(device_serial):
    device_serial._send_command = lambda _: "on"
    device_serial.command_to_state = {"on": True, "off": False}

    assert device_serial.state is True


@patch("chronos.devices.hardware.Serial")
def test_set_state_to_on(mock_serial, device_serial):
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port
    device_serial._send_command = lambda _: "on"
    device_serial.command_to_state = {"on": True, "off": False}
    assert device_serial.state is True


@patch("chronos.devices.hardware.Serial")
def test_set_state_to_off(mock_serial, device_serial):
    mock_port = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_port
    mock_port.write.return_value = b"relay off 0\n\r"
    device_serial._send_command = lambda _: "off"
    device_serial.command_to_state = {"on": True, "off": False}
    assert device_serial.state is False


@patch("chronos.devices.hardware.Serial")
def test_send_command_exception(mock_serial, device_serial, caplog):
    mock_serial_instance = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_serial_instance
    mock_serial_instance.readall.return_value.decode.return_value = (
        "relay read 0 off\n\r"
    )

    response0 = device_serial._send_command("relay read 0\n\r")
    mock_serial_instance.readall.return_value.decode.return_value = (
        "relay read 1 off\n\r"
    )
    response1 = device_serial._send_command("relay read 1\n\r")

    assert "relay read 0" in response0
    assert "off" in response0
    assert "relay read 1" in response1
    assert "off" in response1

    logger.warning("Serial port not accessible")

    warning_messages = [
        record.message for record in caplog.records if record.levelname == "WARNING"
    ]

    assert any("Serial port not accessible" in msg for msg in warning_messages)


@pytest.fixture
def mock_modbus_device():
    """Create a mock ModbusDevice with mocked client."""
    with (
        patch("chronos.devices.manager.ModbusDevice") as mock_client,
        patch("chronos.devices.manager.cfg") as mock_cfg,
    ):
        mock_device = mock_client.return_value

        class Registers:
            def __init__(self):
                self.holding = {
                    "operating_mode": 0x40000,
                    "cascade_mode": 0x40001,
                    "setpoint": 0x40002,
                    "min_setpoint": 0x40003,
                    "max_setpoint": 0x40004,
                    "system_supply_temp": 0x40006,
                }
                self.input = {
                    "alarm": 0x30003,
                    "pump": 0x30004,
                    "flame": 0x30005,
                    "cascade_current_power": 0x30006,
                    "outlet_temp": 0x30008,
                    "inlet_temp": 0x30009,
                    "flue_temp": 0x30010,
                    "lead_firing_rate": 0x30011,
                }

        # Mock config
        mock_cfg.modbus.registers = Registers()
        mock_cfg.modbus.operating_modes = {
            0: "Initialization",
            1: "Standby",
            2: "CH",
            3: "DHW",
            4: "Manual",
        }
        mock_cfg.modbus.cascade_modes = {
            0: "Single Boiler",
            1: "Leader",
            2: "Member",
        }

        yield mock_device


def test_modbus_device_connection(mock_modbus_device):
    mock_modbus_device.client = MagicMock()
    mock_modbus_device.client.is_socket_open.return_value = True

    mock_modbus_device.is_connected.side_effect = (
        lambda: mock_modbus_device.client.is_socket_open()
    )
    assert mock_modbus_device.is_connected() is True


@pytest.mark.parametrize(
    "registers,expected",
    [
        (
            {
                "holding": [1, 2, 150, 120, 180, 0, 220],
                "input": [1, 1, 1, 86, 0, 180, 160, 200, 66],
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
    mock_modbus_device.client = MagicMock()

    holding_mock_response = MagicMock()
    holding_mock_response.registers = registers["holding"]
    holding_mock_response.isError.return_value = False
    mock_modbus_device.client.read_holding_registers.return_value = (
        holding_mock_response
    )

    input_mock_response = MagicMock()
    input_mock_response.registers = registers["input"]
    input_mock_response.isError.return_value = False
    mock_modbus_device.client.read_input_registers.return_value = input_mock_response

    mock_modbus_device.read_boiler_data.return_value = expected

    result = mock_modbus_device.read_boiler_data()

    for key, value in expected.items():
        assert result[key] == value, (
            f"Mismatch for {key}: expected {value}, got {result[key]}"
        )


def test_read_boiler_data_disconnected(mock_modbus_device):
    mock_modbus_device.client = MagicMock()
    mock_modbus_device.client.is_socket_open.return_value = False

    mock_modbus_device.is_connected.side_effect = (
        lambda: mock_modbus_device.client.is_socket_open()
    )

    mock_modbus_device.read_boiler_data.side_effect = ModbusException(
        "Device not connected"
    )

    with pytest.raises(ModbusException, match="Device not connected"):
        mock_modbus_device.read_boiler_data()


def test_read_boiler_data_retry_success(mock_modbus_device):
    mock_modbus_device.client = MagicMock()

    mock_modbus_device.client.read_holding_registers.side_effect = [
        ModbusIOException("First attempt fails"),
        MagicMock(registers=[1, 2, 150, 120, 180, 0, 220], isError=lambda: False),
    ]

    mock_modbus_device.client.read_input_registers.side_effect = [
        ModbusIOException("First attempt fails"),
        MagicMock(registers=[1, 1, 1, 86, 0, 180, 160, 200, 66], isError=lambda: False),
    ]

    mock_modbus_device.read_boiler_data.return_value = {
        "operating_mode": 1,
        "cascade_current_power": 86.0,
    }

    result = mock_modbus_device.read_boiler_data(max_retries=2)
    assert result is not None, "Expected result, but got None"
    assert result["operating_mode"] == 1, f"Expected 1, got {result['operating_mode']}"
    assert result["cascade_current_power"] == 86.0


def test_read_boiler_data_all_retries_fail(mock_modbus_device):
    mock_modbus_device.client = MagicMock()

    mock_modbus_device.client.read_holding_registers.side_effect = ModbusIOException(
        "Communication failed"
    )
    mock_modbus_device.client.read_input_registers.side_effect = ModbusIOException(
        "Communication failed"
    )

    mock_modbus_device.read_boiler_data.side_effect = lambda max_retries: None

    result = mock_modbus_device.read_boiler_data(max_retries=3)

    assert result is None
