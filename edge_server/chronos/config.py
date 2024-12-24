import json
import os
import sys
from pathlib import Path
from .boiler_modbus import MODBUS
MODBUS = {
    "modbus": {
        "port": "/dev/null",  # Use mock device for testing
        "baudrate": 19200,
        "parity": "N",
        "stopbits": 1,
        "bytesize": 8,
        "timeout": 1
    }
}
config_dict = {
    **MODBUS,
    "serial": {
        "baudr": 19200,
        "portname": "/dev/null"
    },
    "sensors": {
        "mount_point": os.getenv("W1_MOUNT_POINT", "/sys/bus/w1/devices"),
        "in_id": "28-00000677d509",
        "out_id": "28-011927cd8e7d",
    },
    "files": {
        "log_path": "/var/log/chronos/chronos.log"
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
        "led_blue": 10
    },
    "efficiency": {
        "hours": 12
    }
}
def ensure_log_path(path: Path):
    candidates = [
        path,
        Path.cwd() / path.name,
        Path("/tmp") / path.name
    ]
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # Test writing the file to ensure we have permission
            with p.open('a'):
                pass
            return p
        except Exception as e:
            print(f"Warning:log file won't work at {p}: {e}")

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

    def get(self, key, default=None):
        """Dictionary-like get method."""
        return getattr(self, key, default)

    def __len__(self):
        """Return number of attributes."""
        return len(vars(self))

    def __getitem__(self, key):
        """Dictionary-like access."""
        return getattr(self, key)

    def items(self):
        """Dictionary-like items method."""
        return vars(self).items()

config_dict["files"]["log_path"] = ensure_log_path(Path(config_dict["files"]["log_path"]))
cfg = Struct(config_dict)
