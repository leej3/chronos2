import random


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
    return {
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


def mock_operating_status():
    return {
        "status": random.choice(["running", "idle", "off"]),
        "setpoint_temperature": random.uniform(70, 110),
        "current_temperature": random.uniform(70, 110),
        "pressure": random.uniform(1.5, 3.0),
        "error_code": (
            None if random.choice([True, False]) else random.randint(1000, 9999)
        ),
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 90.0,
    }


def mock_error_history():
    return {
        "last_lockout_code": 3,
        "last_lockout_str": "Low Water",
        "last_blockout_code": 8,
        "last_blockout_str": "Sensor Failure",
    }


def mock_error_history_none():
    return {
        "last_lockout_code": None,
        "last_lockout_str": None,
        "last_blockout_code": None,
        "last_blockout_str": None,
    }


def history_none():
    return True


def mock_model_info():
    return {
        "model_id": 1,
        "model_name": "FTXL 85",
        "firmware_version": "1.2",
        "hardware_version": "3.4",
    }


def mock_point_update():
    return True
