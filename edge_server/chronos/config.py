import json
import os
from pathlib import Path
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
        "registers": {
            "holding": {
                "operating_mode": 0,    # 40001
                "cascade_mode": 1,      # 40002
                "setpoint": 2,         # 40003
                "min_setpoint": 3,     # 40004 Minimum allowed setpoint
                "max_setpoint": 4,     # 40005 Maximum allowed setpoint
                "supply_temp": 6,      # 40006
                "dhw_temp": 7,         # 40007 Domestic Hot Water temperature
                "last_lockout": 9,     # 40010 Last lockout code
                "last_blockout": 10,   # 40011 Last blockout code
                "anti_cond_temp": 11,  # 40012 Anti-condensation temperature
                "anti_cond_time": 12,  # 40013 Anti-condensation time
                "min_modulation": 13,  # 40014 Minimum modulation rate
                "max_modulation": 14,  # 40015 Maximum modulation rate
                "model_id": 20,        # 40021 Model identification number
                "firmware_ver": 21,    # 40022 Firmware version
                "hardware_ver": 22,    # 40023 Hardware version
            },
            "input": {
                "alarm": 3,            # 30003
                "pump": 4,             # 30004
                "flame": 5,            # 30005
                "cascade_power": 6,     # 30006
                "water_flow": 7,       # 30007
                "outlet_temp": 8,      # 30008
                "inlet_temp": 9,       # 30009
                "flue_temp": 10,       # 30010
                "firing_rate": 11,     # 30011
                "runtime": 12,         # 30012
                "ignition_count": 13,  # 30013 Number of successful ignitions
                "fault_count": 14,     # 30014 Number of faults
                "fan_speed": 15,      # 30015 Current fan speed in RPM
                "fan_setpoint": 16,   # 30016 Fan speed setpoint in RPM
            }
        },
        "operating_modes": {
            "0": "Initialization",
            "1": "Standby",
            "2": "CH Demand",  # Central Heat Demand
            "3": "DHW Demand",  # Domestic Hot Water Demand
            "4": "CH & DHW Demand",
            "5": "Manual Operation",
            "6": "Shutdown",
            "7": "Error",
            "8": "Manual Operation 2",
            "9": "Freeze Protection",
            "10": "Sensor Test"
        },
        "cascade_modes": {
            "0": "Single Boiler",
            "1": "Manager",
            "2": "Member"
        },
        "error_codes": {
            "0": "No Error",
            "1": "Ignition Failure",
            "2": "False Flame",
            "3": "Low Water",
            "4": "Air Flow/Pressure Switch",
            "5": "High Limit",
            "6": "Stack High Limit",
            "7": "System High Limit",
            "8": "Sensor Failure",
            "9": "Fan Speed",
            "10": "Gas Pressure",
            "11": "Water Pressure",
            "12": "Condensate",
            "13": "Flow Switch",
            "14": "DHW High Limit",
            "15": "External Limit",
            "16": "Internal Error",
            "17": "Invalid Parameter",
            "18": "Flame Circuit",
            "19": "Low Power",
            "20": "High Water",
            "21": "High Gas Pressure",
            "22": "Low Gas Pressure",
            "23": "Blocked Drain",
            "24": "Rod Error",
            "25": "Missing Earth",
            "26": "Pilot Error",
            "27": "Valve Error",
            "28": "Burner Error"
        },
        "model_ids": {
            "1": "FTXL 85",
            "2": "FTXL 105",
            "3": "FTXL 125",
            "4": "FTXL 150",
            "5": "FTXL 185",
            "6": "FTXL 220",
            "7": "FTXL 260",
            "8": "FTXL 300",
            "9": "FTXL 399"
        }
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
    "db": {
        "path": "/home/pi/chronos_db/chronos.sql"
    },
    "efficiency": {
        "hours": 12
    }
}

class Struct:
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

import random
sensors = config_dict["sensors"]
mount_point = sensors["mount_point"]
for name,sensor in sensors.items():
    spath = Path(mount_point, sensor, "w1_slave")
    spath.parent.mkdir(parents=True, exist_ok=True)
    spath.write_text(f"YES\nt={random.randint(100,140)}")
cfg = Struct(config_dict)
