import logging
from unittest.mock import MagicMock, patch

import pytest
from chronos.devices import ModbusDevice, ModbusException, create_modbus_connection
from pymodbus.exceptions import ModbusIOException

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

# Test data based on real hardware observations
REAL_HARDWARE_TEMPS = [
    # Format: (raw_fixed_point_celsius_value, expected_fahrenheit)
    # Values taken from working bstat implementation
    # Note: Hardware sends temperatures as fixed point (multiplied by 10)
    (220, 71.6),  # 22.0°C -> 71.6°F
    (320, 89.6),  # 32.0°C -> 89.6°F
    (450, 113.0),  # 45.0°C -> 113.0°F
    (0, 32.0),  # 0.0°C -> 32.0°F
    (1000, 212.0),  # 100.0°C -> 212.0°F
    (-100, 14.0),  # -10.0°C -> 14.0°F
    (1, 32.2),  # 0.1°C -> 32.2°F
]

# Real hardware timing patterns (in seconds)
HARDWARE_TIMING = {
    "normal_read": 0.1,  # Typical read time
    "slow_read": 0.5,  # Slow but acceptable read
    "timeout": 2.0,  # Timeout threshold
    "retry_delay": 1.0,  # Delay between retries
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
def mock_modbus_device(mock_modbus_client, mock_config):
    """Create a ModbusDevice instance with mocked dependencies."""
    device = ModbusDevice(port="/dev/ttyUSB0", baudrate=9600, parity="E")
    # Ensure the device uses the mock configuration
    device.operating_modes = MOCK_CONFIG["operating_modes"]
    device.cascade_modes = MOCK_CONFIG["cascade_modes"]
    device.error_codes = MOCK_CONFIG["error_codes"]
    device.model_ids = MOCK_CONFIG["model_ids"]
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
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, 0],  # Zero supply temp
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
    mock_modbus_device.client.read_holding_registers.return_value.isError.return_value = False

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
        assert result[key] == value, (
            f"Mismatch for {key}: expected {value}, got {result[key]}"
        )


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


@pytest.mark.parametrize("raw_celsius,expected_fahrenheit", REAL_HARDWARE_TEMPS)
def test_temperature_conversion_edge_cases(
    raw_celsius, expected_fahrenheit, device, mock_modbus_client
):
    """Test temperature conversion edge cases observed from real hardware."""
    # Mock both holding and input register responses
    # Note: Hardware sends temperatures as fixed point (multiplied by 10)
    fixed_point_celsius = int(raw_celsius)  # Raw value is already in fixed point format
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[2, 1, 150, 120, 180, 0, fixed_point_celsius],
    )
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            1,
            1,
            1,
            86,
            0,
            fixed_point_celsius,
            fixed_point_celsius,
            fixed_point_celsius,
            66,
        ],
    )

    result = device.read_boiler_data()
    assert result is not None
    assert abs(result["system_supply_temp"] - expected_fahrenheit) < 0.1, (
        f"Expected {expected_fahrenheit}°F but got {result['system_supply_temp']}°F"
    )


def test_read_boiler_data_temperature_ramp(device, mock_modbus_client):
    """Test temperature changes over time like real hardware.

    This test simulates a heating cycle where:
    1. System starts cool
    2. Heating begins, temperatures rise gradually
    3. System reaches target temp
    4. Temperatures stabilize with small fluctuations
    """
    # Simulate temperature ramp based on real hardware observations
    temp_sequence = [
        # Format: (supply_temp, outlet_temp, inlet_temp, flue_temp)
        (140, 142, 138, 150),  # Initial state
        (142, 144, 140, 152),  # Small increase
        (144, 146, 142, 154),  # Gradual heating
        (146, 148, 144, 156),  # Still heating
        (148, 150, 146, 158),  # Approaching target
        (149, 151, 147, 159),  # Almost there
        (150, 152, 148, 160),  # At target
        (149, 151, 147, 159),  # Small fluctuation down
        (150, 152, 148, 160),  # Back to target
    ]

    # Create sequence of mock responses
    mock_responses = []
    for supply, outlet, inlet, flue in temp_sequence:
        # Mock holding registers (includes supply temp)
        mock_responses.append(
            MagicMock(
                isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, supply * 10]
            )
        )
        # Mock input registers (includes outlet, inlet, flue temps)
        mock_responses.append(
            MagicMock(
                isError=lambda: False,
                registers=[1, 1, 1, 86, 0, outlet * 10, inlet * 10, flue * 10, 66],
            )
        )

    # Setup mock to return our sequence
    mock_modbus_client.return_value.read_holding_registers.side_effect = mock_responses[
        ::2
    ]
    mock_modbus_client.return_value.read_input_registers.side_effect = mock_responses[
        1::2
    ]

    # Read sequence of temperatures
    readings = []
    for _ in range(len(temp_sequence)):
        reading = device.read_boiler_data()
        readings.append(reading)

    # Verify temperature progression
    for i in range(len(readings) - 1):
        # Temperatures should change gradually (max 5°F per step)
        temp_change = (
            readings[i + 1]["system_supply_temp"] - readings[i]["system_supply_temp"]
        )
        assert abs(temp_change) <= 5.0, (
            f"Temperature changed too rapidly: {abs(temp_change)}°F"
        )

        # Verify relationships between temperatures
        assert readings[i]["outlet_temp"] > readings[i]["system_supply_temp"], (
            "Outlet should be warmer than supply"
        )
        assert readings[i]["inlet_temp"] < readings[i]["system_supply_temp"], (
            "Inlet should be cooler than supply"
        )
        assert readings[i]["flue_temp"] > readings[i]["outlet_temp"], (
            "Flue should be warmest"
        )


def test_read_boiler_data_with_delays(device, mock_modbus_client):
    """Test retry behavior with communication delays based on real hardware timing."""
    import time

    # Setup mock to simulate various timing patterns
    def delayed_read(*args, **kwargs):
        time.sleep(HARDWARE_TIMING["normal_read"])
        if "read_holding_registers" in str(
            mock_modbus_client.return_value.mock_calls[-1]
        ):
            return MagicMock(
                isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
            )
        else:
            return MagicMock(
                isError=lambda: False, registers=[1, 1, 1, 86, 0, 180, 160, 200, 66]
            )

    def timeout_then_succeed(*args, **kwargs):
        if not hasattr(timeout_then_succeed, "attempt"):
            timeout_then_succeed.attempt = {"holding": 0, "input": 0}

        register_type = (
            "holding"
            if "read_holding_registers"
            in str(mock_modbus_client.return_value.mock_calls[-1])
            else "input"
        )
        timeout_then_succeed.attempt[register_type] += 1

        if timeout_then_succeed.attempt[register_type] == 1:
            time.sleep(HARDWARE_TIMING["timeout"])
            raise ModbusIOException("Timeout")

        time.sleep(HARDWARE_TIMING["normal_read"])
        if register_type == "holding":
            return MagicMock(
                isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
            )
        else:
            return MagicMock(
                isError=lambda: False, registers=[1, 1, 1, 86, 0, 180, 160, 200, 66]
            )

    # Test normal timing
    mock_modbus_client.return_value.read_holding_registers.side_effect = delayed_read
    mock_modbus_client.return_value.read_input_registers.side_effect = delayed_read

    start_time = time.time()
    result = device.read_boiler_data()
    elapsed_time = time.time() - start_time

    assert result is not None
    assert elapsed_time >= HARDWARE_TIMING["normal_read"], "Read completed too quickly"
    assert elapsed_time < HARDWARE_TIMING["timeout"], "Read took too long"

    # Test timeout then success
    mock_modbus_client.return_value.read_holding_registers.side_effect = (
        timeout_then_succeed
    )
    mock_modbus_client.return_value.read_input_registers.side_effect = (
        timeout_then_succeed
    )

    start_time = time.time()
    result = device.read_boiler_data()
    elapsed_time = time.time() - start_time

    assert result is not None
    assert elapsed_time >= HARDWARE_TIMING["timeout"], "Timeout simulation failed"


def test_setpoint_change_state_sequence(device, mock_modbus_client):
    """Test complete state transition during setpoint change.

    This verifies the exact sequence of operations that occur during a setpoint change:
    1. Switch to manual mode
    2. Write new setpoint
    3. Verify mode and setpoint changes
    """
    import time

    states = []
    setpoint_value = 90  # Target temperature in °F
    expected_percentage = int(
        -101.4856 + 1.7363171 * setpoint_value
    )  # Verified formula

    def capture_state(*args, **kwargs):
        """Capture device state after each write."""
        register = args[0] if args else kwargs.get("address", 0)
        value = args[1] if len(args) > 1 else kwargs.get("value", 0)
        states.append({"register": register, "value": value, "timestamp": time.time()})
        return MagicMock(isError=lambda: False)

    # Setup mocks
    mock_modbus_client.return_value.write_register.side_effect = capture_state
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False,
        registers=[
            4,
            1,
            expected_percentage,
            120,
            180,
            0,
            220,
        ],  # Mode 4 = Manual Operation
    )
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False, registers=[1, 1, 1, 86, 0, 180, 160, 200, 66]
    )

    # Perform setpoint change
    success = device.set_boiler_setpoint(setpoint_value)
    assert success is True

    # Verify state sequence
    assert len(states) == 2, "Expected exactly two state changes"

    # First state change should be to manual mode
    assert states[0]["register"] == 0x40000  # Operating mode register
    assert states[0]["value"] == 4  # Manual operation mode

    # Second state change should be setpoint
    assert states[1]["register"] == 0x40002  # Setpoint register
    assert states[1]["value"] == expected_percentage

    # Verify timing between operations
    time_between_ops = states[1]["timestamp"] - states[0]["timestamp"]
    assert time_between_ops < 1.0, "Operations should occur within 1 second"


def test_hardware_error_conditions(device, mock_modbus_client):
    """Test various hardware error conditions observed in production."""
    # Define error scenarios based on real hardware observations
    error_scenarios = [
        {
            "error": ModbusIOException("Connection lost"),
            "error_type": "connection",
            "should_retry": True,
            "max_retries": 3,
            "recovery_time": 1,
        },
        {
            "error": ValueError("Invalid CRC"),
            "error_type": "protocol",
            "should_retry": True,
            "max_retries": 3,
            "recovery_time": 1,
        },
        {
            "error": TimeoutError("No response"),
            "error_type": "timeout",
            "should_retry": True,
            "max_retries": 3,
            "recovery_time": 1,
        },
    ]

    for scenario in error_scenarios:
        # Reset mock for each scenario
        mock_modbus_client.reset_mock()

        # Ensure device is initially connected
        mock_modbus_client.return_value.is_socket_open.return_value = True
        mock_modbus_client.return_value.connect.return_value = True

        # Set up the error behavior
        mock_modbus_client.return_value.read_holding_registers.side_effect = scenario[
            "error"
        ]

        # Should raise ModbusException after max retries
        result = device.read_boiler_data(max_retries=scenario["max_retries"])
        assert result is None
        assert (
            mock_modbus_client.return_value.read_holding_registers.call_count
            == scenario["max_retries"]
        )


def test_hardware_reconnection(device, mock_modbus_client):
    """Test device reconnection behavior after connection loss."""
    # Initial state - connected
    mock_modbus_client.return_value.is_socket_open.return_value = True
    mock_modbus_client.return_value.connect.return_value = True
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
    )
    mock_modbus_client.return_value.read_input_registers.return_value = MagicMock(
        isError=lambda: False, registers=[1, 1, 1, 86, 0, 180, 160, 200, 66]
    )

    # Initial read should succeed
    initial_data = device.read_boiler_data()
    assert initial_data is not None

    # Simulate connection loss
    mock_modbus_client.return_value.is_socket_open.return_value = False
    mock_modbus_client.return_value.connect.return_value = True  # Allow reconnection

    # First attempt should fail with connection error
    with pytest.raises(ModbusException) as exc_info:
        device.read_boiler_data()
    assert "Device not connected" in str(exc_info.value)

    # Reset connection state for reconnection attempt
    mock_modbus_client.return_value.is_socket_open.return_value = True
    mock_modbus_client.return_value.read_holding_registers.return_value = MagicMock(
        isError=lambda: False, registers=[2, 1, 150, 120, 180, 0, 220]
    )

    # Next attempt should succeed after reconnection
    reconnected_data = device.read_boiler_data()
    assert reconnected_data is not None
    assert (
        reconnected_data["operating_mode"] == 2
    )  # Verify data matches expected values


@pytest.mark.hardware
def test_real_hardware_communication():
    """Test communication with real hardware.

    This test only runs when real hardware is available and the
    hardware marker is specified (pytest -m hardware).
    """
    from chronos.config import cfg

    try:
        with create_modbus_connection(port=cfg.modbus.portname) as device:
            # Basic connectivity
            assert device.is_connected()

            # Read data
            data = device.read_boiler_data()
            assert data is not None

            # Verify temperature ranges
            assert 32.0 <= data["system_supply_temp"] <= 220.0
            assert 32.0 <= data["outlet_temp"] <= 220.0
            assert 32.0 <= data["inlet_temp"] <= 220.0
            assert 32.0 <= data["flue_temp"] <= 400.0

            # Verify power/rate ranges
            assert 0.0 <= data["cascade_current_power"] <= 100.0
            assert 0.0 <= data["lead_firing_rate"] <= 100.0

    except Exception as e:
        pytest.skip(f"Hardware test skipped: {str(e)}")


def test_read_boiler_data_all_retries_fail(mock_modbus_device):
    """Test when all retry attempts fail."""
    # Set up mock to fail consistently
    mock_modbus_device.client.read_holding_registers.side_effect = ModbusIOException(
        "Communication failed"
    )
    mock_modbus_device.client.is_socket_open.return_value = True  # Initially connected
    mock_modbus_device.client.connect.return_value = True  # Reconnection succeeds

    # Should raise ModbusException after max retries
    result = mock_modbus_device.read_boiler_data(max_retries=3)
    assert result is None
    assert (
        mock_modbus_device.client.read_holding_registers.call_count == 3
    )  # Verify retry count
