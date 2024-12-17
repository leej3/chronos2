from loguru import logger
from .constants import MODBUS_REGISTERS, SERIAL_COMMANDS, MODES, TEMP_LIMITS

# Import mock or real handlers based on environment
try:
    from .mock_hardware import MockSerialHandler as SerialHandler
    from .mock_hardware import MockModbusHandler as ModbusHandler
    logger.info("Using mock hardware handlers for testing")
except ImportError:
    from .serial_handler import SerialHandler
    from .modbus_handler import ModbusHandler
    logger.info("Using real hardware handlers")

class HVACController:
    def __init__(self):
        self.serial = SerialHandler()
        self.modbus = ModbusHandler()
        self.initialize()
        
    def initialize(self):
        try:
            self.serial.connect()
            self.modbus.connect()
            logger.info("HVAC Controller initialized")
        except Exception as e:
            logger.error(f"Failed to initialize HVAC Controller: {e}")
            raise
            
    def get_state(self):
        try:
            # Get system status via serial
            self.serial.write_data(SERIAL_COMMANDS['GET_STATUS'].encode())
            serial_status = self.serial.read_data()
            
            # Get temperatures and status via Modbus
            state = {
                'chiller_status': self.modbus.read_register(MODBUS_REGISTERS['CHILLER_STATUS']),
                'boiler_status': self.modbus.read_register(MODBUS_REGISTERS['BOILER_STATUS']),
                'temperature_1': self.modbus.read_register(MODBUS_REGISTERS['TEMP_SENSOR_1']) / 10.0,
                'temperature_2': self.modbus.read_register(MODBUS_REGISTERS['TEMP_SENSOR_2']) / 10.0,
                'humidity': self.modbus.read_register(MODBUS_REGISTERS['HUMIDITY']) / 10.0,
                'system_mode': self.modbus.read_register(MODBUS_REGISTERS['SYSTEM_MODE']),
                'serial_status': serial_status
            }
            return state
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            raise
            
    def set_mode(self, mode: str):
        try:
            mode = mode.upper()
            if mode not in MODES:
                raise ValueError(f"Invalid mode: {mode}. Must be one of {list(MODES.keys())}")
                
            # Update via serial
            command = SERIAL_COMMANDS[f'SET_{mode}'].encode()
            self.serial.write_data(command)
            
            # Update via Modbus
            self.modbus.write_register(
                MODBUS_REGISTERS['SYSTEM_MODE'],
                MODES[mode]
            )
            return True
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            raise
            
    def set_temperature(self, temperature: float):
        try:
            # Validate temperature range
            if not TEMP_LIMITS['MIN'] <= temperature <= TEMP_LIMITS['MAX']:
                raise ValueError(
                    f"Temperature must be between {TEMP_LIMITS['MIN']}°C and {TEMP_LIMITS['MAX']}°C"
                )
            
            # Send temperature command via serial
            command = SERIAL_COMMANDS['SET_TEMP'].format(temperature).encode()
            self.serial.write_data(command)
            return True
        except Exception as e:
            logger.error(f"Error setting temperature: {e}")
            raise
            
    def cleanup(self):
        self.serial.close()
        self.modbus.close()