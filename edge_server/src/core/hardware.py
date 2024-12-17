import RPi.GPIO as GPIO
from loguru import logger
from .schemas import SystemState
from .config import settings
import os
import sys
import time

def c_to_f(t):
    return round(((9.0 / 5.0) * t + 32.0), 1)

class HardwareController:
    def __init__(self):
        self.setup_gpio()
        self.sensors = {}
        self.actuators = {}
        self.initialize_hardware()

    def setup_gpio(self):
        """Initialize GPIO settings"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def initialize_hardware(self):
        """Initialize connection to physical hardware"""
        try:
            for sensor in settings.SENSORS:
                self.sensors[sensor.label] = sensor

            for actuator in settings.ACTUATORS:
                GPIO.setup(actuator.pin, GPIO.OUT)
                self.actuators[actuator.id] = actuator
            
            logger.info("Hardware initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize hardware: {e}")
            raise

    def get_current_state(self) -> SystemState:
        """Get current state of all sensors and actuators"""
        state = {
            "sensors": {},
            "actuators": {}
        }
        
        for label, sensor in self.sensors.items():
            state["sensors"][label] = self._read_temperature_sensor(sensor.id)
        
        for actuator_id, actuator in self.actuators.items():
            state["actuators"][actuator_id] = GPIO.input(actuator.pin)
        
        return SystemState(**state)

    def update_settings(self, settings: dict) -> dict:
        """Update system settings"""
        # Implement settings update logic
        return {"status": "success", "settings": settings}

    def _read_temperature_sensor(sensor_id):
        device_file = os.path.join("/sys/bus/w1/devices", sensor_id, "w1_slave")
        while True:
            try:
                with open(device_file) as content:
                    lines = content.readlines()
            except IOError as e:
                logger.error("Temp sensor error: {}".format(e))
                sys.exit(1)
            else:
                if lines[0].strip()[-3:] == "YES":
                    break
                else:
                    time.sleep(0.2)
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            # Divide by 1000 for proper decimal point
            temp = float(temp_string) / 1000.0
            # Convert to degF
            return c_to_f(temp)