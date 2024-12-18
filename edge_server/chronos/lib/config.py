import json
import os
config_dict = {
    "serial": {
        "baudr": 19200,
        "portname": "/dev/ttyACM0"
    },
    "modbus": {
        "baudr": 9600,
        "portname": "/dev/ttyUSB0",
        "parity": "E",
        "timeout": 1,
        "method": "rtu",
        "unit": 1
    },
    "sensors": {
        "mount_point": os.getenv("W1_MOUNT_POINT", "/sys/bus/w1/devices"),
        "in_id": "28-00000677d509",
        "out_id": "28-0000067841b0"
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
    "db": {
        "path": "/home/pi/chronos_db/chronos.sql"
    },
    "efficiency": {
        "hours": 12
    }
}

class Struct(object):

    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


cfg = Struct(config_dict)
