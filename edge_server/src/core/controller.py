from typing import Dict, Any, List
from loguru import logger
from .config import settings
from .constants import MODBUS_REGISTERS, SERIAL_COMMANDS, MODES, TEMP_LIMITS, COMPONENTS
from .logger import get_logs

# Import real or mock hardware based on configuration
if settings.MOCK_HARDWARE:
    from .hardware.mock_hardware import MockModbusClient as ModbusClient
    from .hardware.mock_hardware import MockSerialClient as SerialClient
    logger.info("Using mock hardware for development")
else:
    from .hardware.modbus_client import ModbusClient
    from .hardware.serial_client import SerialClient
    logger.info("Using real hardware connections")

class HVACController:
    def __init__(self):
        self.modbus = ModbusClient()
        self.serial = SerialClient()
        self.initialize()
        
    def initialize(self):
        """Initialize hardware connections"""
        try:
            self.modbus.connect()
            self.serial.connect()
            logger.info("HVAC Controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HVAC Controller: {e}")
            raise
            
    def get_state(self) -> Dict[str, Any]:
        """Get complete system state"""
        try:
            # Get component states
            components = []
            for comp_id, comp_info in COMPONENTS.items():
                status = self.modbus.read_register(comp_info['register'])
                components.append({
                    'id': comp_info['id'],
                    'type': comp_info['type'],
                    'status': bool(status)
                })

            # Get temperatures
            temps = {}
            for i in range(2):  # Two temperature sensors
                register = MODBUS_REGISTERS['TEMP_SENSOR_BASE'] + i
                temps[f'temp_{i+1}'] = self.modbus.read_register(register) / 10.0

            # Get system mode
            mode_value = self.modbus.read_register(MODBUS_REGISTERS['SYSTEM_MODE'])
            mode = next((k for k, v in MODES.items() if v == mode_value), 'OFF')

            state = {
                'components': components,
                'temperatures': temps,
                'humidity': self.modbus.read_register(MODBUS_REGISTERS['HUMIDITY']) / 10.0,
                'mode': mode
            }
            
            return state
        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            raise

    def set_component_status(self, component_id: str, status: bool) -> bool:
        """Set individual component status"""
        try:
            # Find component in configuration
            component = next(
                (comp for comp in COMPONENTS.values() if comp['id'] == component_id),
                None
            )
            if not component:
                raise ValueError(f"Invalid component ID: {component_id}")

            # Update via Modbus
            value = 1 if status else 0
            self.modbus.write_register(component['register'], value)

            # Update via Serial
            command = SERIAL_COMMANDS['SET_COMPONENT'].format(component_id, value)
            self.serial.write_data(command)

            logger.info(f"Component {component_id} status set to {status}")
            return True
        except Exception as e:
            logger.error(f"Error setting component status: {e}")
            raise
            
    def set_mode(self, mode: str) -> bool:
        """Set system operation mode"""
        try:
            mode = mode.upper()
            if mode not in MODES:
                raise ValueError(f"Invalid mode: {mode}. Must be one of {list(MODES.keys())}")
                
            # Update via serial
            command = SERIAL_COMMANDS[f'SET_{mode}']
            self.serial.write_data(command)
            
            # Update via Modbus
            self.modbus.write_register(
                MODBUS_REGISTERS['SYSTEM_MODE'],
                MODES[mode]
            )
            
            logger.info(f"System mode changed to {mode}")
            return True
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            raise
            
    def set_temperature(self, temperature: float) -> bool:
        """Set target temperature"""
        try:
            # Validate temperature range
            if not TEMP_LIMITS['MIN'] <= temperature <= TEMP_LIMITS['MAX']:
                raise ValueError(
                    f"Temperature must be between {TEMP_LIMITS['MIN']}°C and {TEMP_LIMITS['MAX']}°C"
                )
            
            # Send temperature command via serial
            command = SERIAL_COMMANDS['SET_TEMP'].format(temperature)
            self.serial.write_data(command)
            
            logger.info(f"Target temperature set to {temperature}°C")
            return True
        except Exception as e:
            logger.error(f"Error setting temperature: {e}")
            raise
            
    def get_logs(self, n_lines: int = 100) -> List[str]:
        """Get system logs"""
        return get_logs(n_lines)
            
    def cleanup(self):
        """Clean up hardware connections"""
        try:
            self.serial.close()
            self.modbus.close()
            logger.info("HVAC Controller cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise