import logging
from unittest.mock import MagicMock, patch

import pytest
from chronos.devices import ModbusDevice, ModbusException, create_modbus_connection

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_device_initialization(mock_modbus_client):
    """Test device initialization and connection."""
    device = ModbusDevice(port="/dev/ttyUSB0", baudrate=9600, parity="E")

    # Verify client initialization
    mock_modbus_client.assert_called_once_with(
        port="/dev/ttyUSB0", baudrate=9600, parity="E", timeout=1
    )

    # Verify connection attempt
    mock_modbus_client.return_value.connect.assert_called_once()

    device.close()
    mock_modbus_client.return_value.close.assert_called_once()


def test_read_boiler_data_success(device, mock_modbus_client):
    """Test successful reading of boiler data with verified values."""
    # Mock holding register responses (mode through supply temp)
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            2,
            1,
            150,
            120,
            180,
            0,
            220,
        ],  # Mode=CH Demand, Cascade=Manager, Setpoints, Supply=22.0°C
    )

    # Mock input register responses (status through firing rate)
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            1,
            1,
            1,
            86,
            0,
            180,
            160,
            200,
            66,
        ],  # Status flags, Power=86%, Temps, Rate=66%
    )

    stats = device.read_boiler_data()

    assert stats is not None
    # Verified working values
    assert stats["operating_mode"] == 2
    assert stats["operating_mode_str"] == "CH Demand"
    assert stats["cascade_mode"] == 1
    assert stats["cascade_mode_str"] == "Manager"
    assert stats["system_supply_temp"] == round((9.0 / 5.0) * (220 / 10.0) + 32.0, 1)
    assert stats["outlet_temp"] == round((9.0 / 5.0) * (180 / 10.0) + 32.0, 1)
    assert stats["inlet_temp"] == round((9.0 / 5.0) * (160 / 10.0) + 32.0, 1)
    assert stats["flue_temp"] == round((9.0 / 5.0) * (200 / 10.0) + 32.0, 1)
    assert stats["cascade_current_power"] == 86.0
    assert stats["lead_firing_rate"] == 66.0
    assert stats["alarm_status"] is True
    assert stats["pump_status"] is True
    assert stats["flame_status"] is True


def test_read_boiler_data_failure(device, mock_modbus_client):
    """Test handling of read failures."""
    # Mock read failure
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: True
    )

    stats = device.read_boiler_data()
    assert stats is None


def test_set_boiler_setpoint_success(device, mock_modbus_client):
    """Test successful setting of boiler setpoint.

    Note: The C implementation uses a specific formula for converting temperature to percentage:
    sp = trunc(-101.4856 + 1.7363171 * temp)

    For example:
    140°F -> 42% (approximately)
    This maps to the boiler's BMS configuration:
    - 2V (0%) -> 70°F
    - 9V (100%) -> 110°F
    """
    # Mock successful write responses
    mock_modbus_client.return_value.write_register.return_value = MagicMock(
        isError=lambda: False
    )

    # Test with 140°F which should map to ~42%
    success = device.set_boiler_setpoint(140)
    assert success is True

    # Verify both writes occurred:
    # 1. Write mode 4 (manual operation) to register 40001
    # 2. Write setpoint percentage to register 40003
    assert mock_modbus_client.return_value.write_register.call_count == 2
    mock_modbus_client.return_value.write_register.assert_any_call(0x40000, 4)  # Mode
    mock_modbus_client.return_value.write_register.assert_any_call(
        0x40002, 42
    )  # Setpoint


def test_set_boiler_setpoint_invalid_range(device, mock_modbus_client):
    """Test setpoint validation.

    The boiler accepts setpoints between 70°F and 110°F, which map to 0-100%.
    Values outside this range should fail.
    """
    # Test temperature too low (below 70°F)
    success = device.set_boiler_setpoint(60)
    assert success is False

    # Test temperature too high (above 110°F)
    success = device.set_boiler_setpoint(120)
    assert success is False

    # Verify no writes were attempted
    mock_modbus_client.return_value.write_register.assert_not_called()


def test_read_operating_status_success(device, mock_modbus_client):
    """Test successful reading of operating status.

    Note: The actual setpoint value comes from a file in the C implementation,
    not from Modbus registers. Our implementation reading it from registers
    is unverified and may not be reliable.
    """
    # Mock register responses with verified values
    mock_modbus_client.return_value.read_holding_registers.side_effect = [
        MagicMock(isError=lambda: False, registers=[2]),  # Operating mode (CH Demand)
        MagicMock(isError=lambda: False, registers=[1]),  # Cascade mode (Manager)
        MagicMock(isError=lambda: False, registers=[150]),  # Setpoint (unverified)
    ]

    status = device.read_operating_status()
    assert status["operating_mode"] == 2
    assert status["operating_mode_str"] == "CH Demand"
    assert status["cascade_mode"] == 1
    assert status["cascade_mode_str"] == "Manager"
    # Note: Setpoint value is unverified as it comes from file in C implementation
    assert "current_setpoint" in status  # Just verify it exists


def test_read_error_history_success(device, mock_modbus_client):
    """Test successful reading of error history.

    Note: This functionality is unverified against the working C implementation.
    These registers may need different scaling or interpretation.
    """
    # Mock register response for lockout and blockout codes
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[3, 8],  # Lockout code 3, Blockout code 8
    )

    history = device.read_error_history()
    assert history["last_lockout_code"] == 3
    assert "Low Water" in history["last_lockout_str"]
    assert history["last_blockout_code"] == 8
    assert "Sensor Failure" in history["last_blockout_str"]


def test_read_model_info_success(device, mock_modbus_client):
    """Test successful reading of model information.

    Note: This functionality is unverified against the working C implementation.
    These registers may need different scaling or interpretation.
    """
    # Mock register response for model info
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            1,  # Model ID (FTXL 85)
            0x0102,  # Firmware version (1.2)
            0x0304,  # Hardware version (3.4)
        ],
    )

    info = device.read_model_info()
    assert info["model_id"] == 1
    assert "FTXL 85" in info["model_name"]
    assert info["firmware_version"] == "1.2"
    assert info["hardware_version"] == "3.4"


def test_connection_context_manager():
    """Test the connection context manager."""
    with patch("chronos.devices.ModbusDevice") as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        mock_device.is_connected.return_value = True

        with create_modbus_connection() as device:
            assert device is mock_device

        mock_device.close.assert_called_once()


def test_connection_context_manager_failure():
    """Test the connection context manager with connection failure."""
    with patch("chronos.devices.ModbusDevice") as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        mock_device.is_connected.return_value = False

        with pytest.raises(ModbusException):
            with create_modbus_connection():
                pass


@pytest.mark.parametrize(
    "temp_value,expected_f",
    [
        (0, 32.0),  # Freezing point
        (1000, 212.0),  # Boiling point (100.0°C)
        (-100, -148.0),  # Below freezing
        (2200, 428.0),  # Very hot
        (1, 33.8),  # Small value
        (-1, 30.2),  # Small negative
    ],
)
def test_temperature_conversion(temp_value, expected_f):
    """Test temperature conversion edge cases.

    The C implementation divides register values by 10 before converting,
    so our test values are multiplied by 10 to simulate register values.
    """
    from chronos.devices import c_to_f

    # Simulate register value (multiplied by 10)
    assert round(c_to_f(temp_value / 10.0), 1) == expected_f


def test_read_boiler_data_zero_temps(device, mock_modbus_client):
    """Test handling of zero temperature values.

    The C implementation treats zero temperatures as valid values,
    converting them to their Fahrenheit equivalent (32°F).
    """
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, 0],  # Zero supply temp
    )

    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[1, 1, 1, 86, 0, 0, 0, 0, 66],  # Zero outlet, inlet, flue temps
    )

    stats = device.read_boiler_data()
    assert stats["system_supply_temp"] == 32.0
    assert stats["outlet_temp"] == 32.0
    assert stats["inlet_temp"] == 32.0
    assert stats["flue_temp"] == 32.0


def test_read_boiler_data_power_edge_cases(device, mock_modbus_client):
    """Test edge cases for power and firing rate values.

    The C implementation treats these as direct percentages with no conversion.
    Values should be clamped between 0-100%.
    """
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, 220],
    )

    test_cases = [
        ([1, 1, 1, 0, 0, 180, 160, 200, 0], 0.0, 0.0),  # Min power/rate
        ([1, 1, 1, 100, 0, 180, 160, 200, 100], 100.0, 100.0),  # Max power/rate
        ([1, 1, 1, 50, 0, 180, 160, 200, 50], 50.0, 50.0),  # Mid power/rate
    ]

    for input_regs, expected_power, expected_rate in test_cases:
        mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
            isError=lambda: False,
            registers=input_regs,
        )
        stats = device.read_boiler_data()
        assert stats["cascade_current_power"] == expected_power
        assert stats["lead_firing_rate"] == expected_rate


def test_read_boiler_data_status_combinations(device, mock_modbus_client):
    """Test various combinations of status flags.

    The C implementation reads these as direct boolean values from bits.
    We should test various combinations of on/off states.
    """
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, 220],
    )

    test_cases = [
        ([0, 0, 0, 86, 0, 180, 160, 200, 66], False, False, False),  # All off
        ([1, 1, 1, 86, 0, 180, 160, 200, 66], True, True, True),  # All on
        ([1, 0, 1, 86, 0, 180, 160, 200, 66], True, False, True),  # Mixed 1
        ([0, 1, 0, 86, 0, 180, 160, 200, 66], False, True, False),  # Mixed 2
    ]

    for input_regs, exp_alarm, exp_pump, exp_flame in test_cases:
        mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
            isError=lambda: False,
            registers=input_regs,
        )
        stats = device.read_boiler_data()
        assert stats["alarm_status"] is exp_alarm
        assert stats["pump_status"] is exp_pump
        assert stats["flame_status"] is exp_flame


def test_read_boiler_data_partial_failure(device, mock_modbus_client):
    """Test handling of partial read failures.

    Test what happens when one register read succeeds but another fails.
    The C implementation treats this as a complete failure.
    """
    # Mock holding registers success
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, 220],
    )

    # Mock input registers failure
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: True
    )

    stats = device.read_boiler_data()
    assert stats is None

    # Test the reverse case
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: True
    )
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[1, 1, 1, 86, 0, 180, 160, 200, 66],
    )

    stats = device.read_boiler_data()
    assert stats is None
