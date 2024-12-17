import RPi.GPIO as GPIO
from loguru import logger
from .schemas import SystemState
from .config import settings

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
                GPIO.setup(sensor.pin, GPIO.IN)
                self.sensors[sensor.id] = sensor

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
        
        for sensor_id, sensor in self.sensors.items():
            state["sensors"][sensor_id] = GPIO.input(sensor.pin)
        
        for actuator_id, actuator in self.actuators.items():
            state["actuators"][actuator_id] = GPIO.input(actuator.pin)
        
        return SystemState(**state)

    def switch_mode(self, mode: str) -> dict:
        """Switch system operation mode"""
        # Implement mode switching logic
        return {"status": "success", "mode": mode}

    def update_settings(self, settings: dict) -> dict:
        """Update system settings"""
        # Implement settings update logic
        return {"status": "success", "settings": settings}

    def __del__(self):
        """Cleanup GPIO on object destruction"""
        GPIO.cleanup()