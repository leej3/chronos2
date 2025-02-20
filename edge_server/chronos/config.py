import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .boiler_modbus import MODBUS

load_dotenv()


def ensure_log_path(path: Path):
    candidates = [path, Path.cwd() / path.name, Path("/tmp") / path.name]
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # Test writing the file to ensure we have permission
            with p.open("a"):
                pass
            print(f"Using log file at {p}")
            return p
        except Exception as e:
            print(f"Log file won't work at {p}: {e}")

    # If all fail, exit or raise an exception
    print("Could not create a suitable log file path.")
    sys.exit(1)


class Struct:
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


config_dict = {
    **MODBUS,
    "serial": {"baudr": 19200, "portname": "/dev/ttyACM0"},
    "sensors": {
        "mount_point": "/sys/bus/w1/devices",
        "in_id": "28-00000677d509",
        "out_id": "28-011927cd8e7d",
    },
    "files": {
        "log_path": str(ensure_log_path(Path("/opt/chronos/edge_server/chronos.log")))
    },
    "relay": {
        "boiler": 0,
        "chiller1": 2,
        "chiller2": 1,
        "chiller3": 4,
        "chiller4": 3,
        "winter_valve": 5,
        "summer_valve": 6,
        "led_breather": 7,
        "led_red": 8,
        "led_green": 9,
        "led_blue": 10,
    },
    "efficiency": {"hours": 12},
    "temperature": {
        "min_setpoint": float(os.getenv("MIN_SETPOINT_TEMP", "70.0")),
        "max_setpoint": float(os.getenv("MAX_SETPOINT_TEMP", "110.0")),
    },
    "MOCK_DEVICES": os.getenv("MOCK_DEVICES", "false").lower() == "true",
    "READ_ONLY_MODE": os.getenv("READ_ONLY_MODE", "false").lower() == "true",
    "registers": {
        "holding": {
            "operating_mode": 0,
            "cascade_mode": 1,
            "setpoint": 2,
            "min_setpoint_limit": 3,
            "max_setpoint_limit": 4,
            "last_lockout": 5,
            "system_supply_temp": 6,
            "model_id": 7,
            "firmware_version": 8,
            "hardware_version": 9,
            "last_lockout_code": 10,
            "last_blockout_code": 11,
        },
        "input": {
            "alarm": 0,
            "pump": 1,
            "flame": 2,
            "cascade_current_power": 3,
            "outlet_temp": 5,
            "inlet_temp": 6,
            "flue_temp": 7,
            "lead_firing_rate": 8,
        },
    },
}
cfg = Struct(config_dict)
