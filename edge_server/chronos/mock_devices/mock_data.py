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
        "operating_mode": 3,
        "operating_mode_str": "Central Heat",
        "cascade_mode": 0,
        "cascade_mode_str": "Single Boiler",
        "current_setpoint": 158.0,
        "status": True,
        "setpoint_temperature": 158.0,
        "current_temperature": 155.5,
        "pressure": 15.2,
        "error_code": 0,
    }


def mock_point_update():
    return True
