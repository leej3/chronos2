import logging
from unittest.mock import MagicMock, patch

import pytest
from chronos.devices import ModbusDevice, ModbusException, create_modbus_connection

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock config mappings
MOCK_CONFIG = {
    "operating_modes": {
        "0": "Initialization",
        "1": "Standby",
        "2": "CH Demand",
        "3": "DHW Demand",
        "4": "Manual Operation",
    },
    "cascade_modes": {
        "0": "Single Boiler",
        "1": "Manager",
        "2": "Member",
    },
    "error_codes": {
        "0": "No Error",
        "1": "Ignition Failure",
        "2": "Safety Circuit Open",
        "3": "Low Water",
        "4": "Gas Pressure Error",
        "5": "High Limit",
        "6": "Flame Circuit Error",
        "7": "Sensor Failure",
        "8": "Fan Speed Error",
    },
    "model_ids": {
        "1": "FTXL 85",
        "2": "FTXL 105",
        "3": "FTXL 125",
    },
}


@pytest.fixture
def mock_config():
    """Mock the config module."""
    with patch("chronos.devices.cfg") as mock_cfg:
        # Create a mock Struct-like object for registers
        class MockRegisters:
            def __init__(self):
                self.holding = type(
                    "Struct",
                    (),
                    {
                        "operating_mode": 0x40000,
                        "cascade_mode": 0x40001,
                        "setpoint": 0x40002,
                        "min_setpoint": 0x40003,
                        "max_setpoint": 0x40004,
                        "last_lockout": 0x40005,
                        "model_id": 0x40006,
                    },
                )()
                self.input = type(
                    "Struct",
                    (),
                    {
                        "alarm": 0x30003,
                        "pump": 0x30004,
                        "flame": 0x30005,
                    },
                )()

        mock_cfg.modbus.registers = MockRegisters()
        mock_cfg.modbus.operating_modes = MOCK_CONFIG["operating_modes"]
        mock_cfg.modbus.cascade_modes = MOCK_CONFIG["cascade_modes"]
        mock_cfg.modbus.error_codes = MOCK_CONFIG["error_codes"]
        mock_cfg.modbus.model_ids = MOCK_CONFIG["model_ids"]
        yield mock_cfg


@pytest.fixture
def device(mock_modbus_client, mock_config):
    """Create a ModbusDevice instance with mocked dependencies."""
    device = ModbusDevice(port="/dev/ttyUSB0", baudrate=9600, parity="E")
    return device


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
            2,  # Mode=CH Demand
            1,  # Cascade=Manager
            150,  # Setpoint (15.0°C)
            120,  # Min Setpoint (12.0°C)
            180,  # Max Setpoint (18.0°C)
            0,  # Reserved
            220,  # Supply Temp (22.0°C)
        ],
    )

    # Mock input register responses (status through firing rate)
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            1,  # Alarm Status
            1,  # Pump Status
            1,  # Flame Status
            86,  # Power=86%
            0,  # Reserved
            180,  # Outlet Temp (18.0°C)
            160,  # Inlet Temp (16.0°C)
            200,  # Flue Temp (20.0°C)
            66,  # Rate=66%
        ],
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


def test_set_boiler_setpoint_success(device, mock_modbus_client):
    """Test successful setting of boiler setpoint.

    Note: The C implementation uses a specific formula for converting temperature to percentage:
    sp = trunc(-101.4856 + 1.7363171 * temp)

    For example:
    90°F -> 54% (calculated using the exact formula)
    This maps to the boiler's BMS configuration:
    - 2V (0%) -> 70°F
    - 9V (100%) -> 110°F
    """
    # Mock successful write responses
    mock_modbus_client.return_value.write_register.return_value = MagicMock(
        isError=lambda: False
    )

    # Test with 90°F which maps to 54%
    success = device.set_boiler_setpoint(90)
    assert success is True

    # Verify both writes occurred:
    # 1. Write mode 4 (manual operation) to register 40001
    # 2. Write setpoint percentage to register 40003
    assert mock_modbus_client.return_value.write_register.call_count == 2
    mock_modbus_client.return_value.write_register.assert_any_call(0x40000, 4)  # Mode
    mock_modbus_client.return_value.write_register.assert_any_call(
        0x40002, 54
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
    """Test successful reading of operating status."""
    # Mock register responses with verified values
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150],  # Mode=CH Demand, Cascade=Manager, Setpoint=15.0°C
    )

    status = device.read_operating_status()
    assert status["operating_mode"] == 2
    assert status["operating_mode_str"] == "CH Demand"
    assert status["cascade_mode"] == 1
    assert status["cascade_mode_str"] == "Manager"
    assert status["current_setpoint"] == round((9.0 / 5.0) * (150 / 10.0) + 32.0, 1)


def test_read_error_history_success(device, mock_modbus_client):
    """Test successful reading of error history."""
    # Mock register response for lockout and blockout codes
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            3,
            8,
        ],  # Lockout code 3 (Low Water), Blockout code 8 (Fan Speed Error)
    )

    history = device.read_error_history()
    assert history["last_lockout_code"] == 3
    assert history["last_lockout_str"] == "Low Water"
    assert history["last_blockout_code"] == 8
    assert history["last_blockout_str"] == "Fan Speed Error"


def test_read_model_info_success(device, mock_modbus_client):
    """Test successful reading of model information."""
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
    assert info["model_name"] == "FTXL 85"
    assert info["firmware_version"] == "1.2"
    assert info["hardware_version"] == "3.4"


@pytest.mark.parametrize(
    "temp_value,expected_f",
    [
        (0, 32.0),  # 0°C -> 32°F
        (100, 212.0),  # 100°C -> 212°F
        (-10, 14.0),  # -10°C -> 14°F
        (220, 428.0),  # 220°C -> 428°F
        (0.1, 32.2),  # 0.1°C -> 32.2°F
        (-0.1, 31.8),  # -0.1°C -> 31.8°F
    ],
)
def test_temperature_conversion(temp_value, expected_f):
    """Test temperature conversion edge cases."""
    from chronos.devices import c_to_f

    assert round(c_to_f(temp_value), 1) == expected_f


def test_read_boiler_data_zero_temps(device, mock_modbus_client):
    """Test handling of zero temperature values."""
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 0]  # Zero supply temp
    )

    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[1, 1, 1, 86, 0, 0, 0, 0, 66],  # Zero outlet, inlet, flue temps
    )

    stats = device.read_boiler_data()
    assert stats["system_supply_temp"] == 32.0  # 0°C -> 32°F
    assert stats["outlet_temp"] == 32.0
    assert stats["inlet_temp"] == 32.0
    assert stats["flue_temp"] == 32.0


def test_read_boiler_data_power_edge_cases(device, mock_modbus_client):
    """Test edge cases for power and firing rate values."""
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
    )

    test_cases = [
        ([1, 1, 1, 0, 0, 180, 160, 200, 0], 0.0, 0.0),  # Min power/rate
        ([1, 1, 1, 100, 0, 180, 160, 200, 100], 100.0, 100.0),  # Max power/rate
        ([1, 1, 1, 50, 0, 180, 160, 200, 50], 50.0, 50.0),  # Mid power/rate
    ]

    for input_regs, expected_power, expected_rate in test_cases:
        mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
            isError=lambda: False, registers=input_regs
        )
        stats = device.read_boiler_data()
        assert stats["cascade_current_power"] == expected_power
        assert stats["lead_firing_rate"] == expected_rate


def test_read_boiler_data_status_combinations(device, mock_modbus_client):
    """Test various combinations of status flags."""
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
    )

    test_cases = [
        ([0, 0, 0, 86, 0, 180, 160, 200, 66], False, False, False),  # All off
        ([1, 1, 1, 86, 0, 180, 160, 200, 66], True, True, True),  # All on
        ([1, 0, 1, 86, 0, 180, 160, 200, 66], True, False, True),  # Mixed 1
        ([0, 1, 0, 86, 0, 180, 160, 200, 66], False, True, False),  # Mixed 2
    ]

    for input_regs, exp_alarm, exp_pump, exp_flame in test_cases:
        mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
            isError=lambda: False, registers=input_regs
        )
        stats = device.read_boiler_data()
        assert stats["alarm_status"] is exp_alarm
        assert stats["pump_status"] is exp_pump
        assert stats["flame_status"] is exp_flame


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
                "Operating Mode": 1,
                "Operating Mode String": "Standby",
                "Cascade Mode": 2,
                "Cascade Mode String": "Member",
                "System Supply Temp": round((9.0 / 5.0) * (220 / 10.0) + 32.0, 1),
                "Outlet Temp": round((9.0 / 5.0) * (180 / 10.0) + 32.0, 1),
                "Inlet Temp": round((9.0 / 5.0) * (160 / 10.0) + 32.0, 1),
                "Flue Temp": round((9.0 / 5.0) * (200 / 10.0) + 32.0, 1),
                "Alarm Status": True,
                "Pump Status": True,
                "Flame Status": True,
                "Cascade Current Power": 86.0,
                "Lead Firing Rate": 66.0,
            },
        ),
        # Test case 2: All zeros/off
        (
            {"holding": [0, 0, 0, 0, 0, 0, 0], "input": [0, 0, 0, 0, 0, 0, 0, 0, 0]},
            {
                "Operating Mode": 0,
                "Operating Mode String": "Initialization",
                "Cascade Mode": 0,
                "Cascade Mode String": "Single Boiler",
                "System Supply Temp": 32.0,
                "Outlet Temp": 32.0,
                "Inlet Temp": 32.0,
                "Flue Temp": 32.0,
                "Alarm Status": False,
                "Pump Status": False,
                "Flame Status": False,
                "Cascade Current Power": 0.0,
                "Lead Firing Rate": 0.0,
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
    assert result["Operating Mode"] == 1
    assert result["Cascade Current Power"] == 86.0
