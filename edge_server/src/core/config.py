from pydantic_settings import BaseSettings
from typing import List
from .schemas import SensorConfig, ActuatorConfig

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Hardware settings
    MOCK_HARDWARE: bool = True  # Set to False in production
    MODBUS_PORT: str = "/dev/ttyUSB0"
    MODBUS_BAUDRATE: int = 9600
    SERIAL_PORT: str = "/dev/ttyUSB1"
    SERIAL_BAUDRATE: int = 9600

    # Hardware configuration
    SENSORS: List[SensorConfig] = [
        SensorConfig(id="temp_1", type="temperature", pin=17),
        SensorConfig(id="temp_2", type="temperature", pin=18)
    ]
    
    ACTUATORS: List[ActuatorConfig] = [
        ActuatorConfig(id="chiller_1", type="chiller", pin=23),
        ActuatorConfig(id="boiler_1", type="boiler", pin=24)
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "hvac.log"

    class Config:
        env_file = ".env"

settings = Settings()