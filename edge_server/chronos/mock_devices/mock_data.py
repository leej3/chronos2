import random

# Mock state storage
_mock_state = {
    "current_setpoint": 158.0,
    "operating_status": {
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "status": True,
        "pressure": 15.2,
        "error_code": 0,
    },
}


def mock_sensors():
    return_temp = random.uniform(10, 80)
    water_out_temp = random.uniform(return_temp - 20, return_temp + 20)
    water_out_temp = max(30, min(water_out_temp, 90))
    return {"return_temp": return_temp, "water_out_temp": water_out_temp}


def mock_devices_data():
    return [
        {"id": 0, "state": True},
        {"id": 1, "state": False},
        {"id": 2, "state": False},
        {"id": 3, "state": False},
        {"id": 4, "state": False},
    ]


def mock_boiler_stats():
    current_setpoint = _mock_state["current_setpoint"]
    return {
        "system_supply_temp": round(current_setpoint - random.uniform(2, 4), 1),
        "outlet_temp": round(current_setpoint + random.uniform(-1, 1), 1),
        "inlet_temp": round(current_setpoint - random.uniform(8, 10), 1),
        "flue_temp": round(current_setpoint + random.uniform(15, 20), 1),
        "cascade_current_power": 50.0,
        "lead_firing_rate": 75.0,
        "water_flow_rate": 10.0,
        "pump_status": True,
        "flame_status": True,
    }


def mock_operating_status():
    status = _mock_state["operating_status"].copy()
    status["current_setpoint"] = _mock_state["current_setpoint"]
    status["setpoint_temperature"] = _mock_state["current_setpoint"]
    status["current_temperature"] = round(
        _mock_state["current_setpoint"] - random.uniform(0, 3), 1
    )
    return status


def mock_point_update(temperature=None):
    """Update mock boiler setpoint and return success."""
    if temperature is not None:
        _mock_state["current_setpoint"] = temperature
    return True
