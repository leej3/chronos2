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
            "operating_mode": 0x40000,  # Base address for holding registers
            "cascade_mode": 0x40001,
            "setpoint": 0x40002,
            "min_setpoint_limit": 0x40003,
            "max_setpoint_limit": 0x40004,
            "last_lockout": 0x40005,
            "model_id": 0x40006,
            "system_supply_temp": 0x40007,
        },
        "input": {
            "alarm": 0x30003,  # Base address for input registers
            "pump": 0x30004,
            "flame": 0x30005,
            "cascade_current_power": 0x30006,
            "outlet_temp": 0x30008,
            "inlet_temp": 0x30009,
            "flue_temp": 0x30010,
            "lead_firing_rate": 0x30011,
        },
    },
}
cfg = Struct(config_dict)
