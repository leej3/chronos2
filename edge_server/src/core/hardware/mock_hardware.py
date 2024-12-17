from loguru import logger
from typing import Dict, Any
from ..constants import MODES, COMPONENTS

class MockModbusClient:
    """Mock implementation of ModbusClient for development/testing"""
    def __init__(self):
        self._connected = False
        self._state = {
            # Initialize component states
            **{comp['register']: 0 for comp in COMPONENTS.values()},
            # Temperature sensors
            0x20: 225,  # 22.5°C
            0x21: 235,  # 23.5°C
            # Other states
            0x40: 450,  # Humidity 45.0%
            0x41: 0     # System mode OFF
        }

    def connect(self) -> bool:
        """Simulate connecting to Modbus RTU"""
        self._connected = True
        logger.info("[MOCK] Connected to Modbus RTU")
        return True

    def read_register(self, address: int, unit: int = 1) -> int:
        """Simulate reading from Modbus register"""
        if not self._connected:
            raise ConnectionError("Not connected")
            
        if address not in self._state:
            raise ValueError(f"Invalid register address: {address}")
            
        return self._state[address]

    def write_register(self, address: int, value: int, unit: int = 1) -> bool:
        """Simulate writing to Modbus register"""
        if not self._connected:
            raise ConnectionError("Not connected")
            
        if address not in self._state:
            raise ValueError(f"Invalid register address: {address}")
            
        self._state[address] = value
        
        # Log component state changes
        component = next(
            (comp for comp in COMPONENTS.values() if comp['register'] == address),
            None
        )
        if component:
            logger.info(f"[MOCK] Component {component['id']} set to {bool(value)}")
                
        return True

    def close(self):
        """Simulate closing Modbus connection"""
        self._connected = False
        logger.info("[MOCK] Closed Modbus connection")


class MockSerialClient:
    """Mock implementation of SerialClient for development/testing"""
    def __init__(self):
        self._connected = False
        self._state = {
            'status': 'RUNNING',
            'temperature': 22.5,
            'components': {comp['id']: False for comp in COMPONENTS.values()}
        }

    def connect(self) -> bool:
        """Simulate connecting to serial port"""
        self._connected = True
        logger.info("[MOCK] Connected to serial port")
        return True

    def read_data(self) -> str:
        """Simulate reading from serial port"""
        if not self._connected:
            raise ConnectionError("Not connected")
            
        components_status = ';'.join(
            f"{comp_id}={int(status)}"
            for comp_id, status in self._state['components'].items()
        )
        return f"STATUS:{self._state['status']};TEMP:{self._state['temperature']};{components_status}"

    def write_data(self, data: str) -> bool:
        """Simulate writing to serial port"""
        if not self._connected:
            raise ConnectionError("Not connected")
            
        logger.info(f"[MOCK] Writing data: {data}")
        
        # Update state based on commands
        if data.startswith('TEMP='):
            try:
                self._state['temperature'] = float(data[5:-2])  # Remove TEMP= and \r\n
            except ValueError:
                pass
        elif 'MODE=' in data:
            mode = data.split('=')[1].strip()
            self._state['status'] = f"MODE_{mode}"
        elif 'COMPONENT=' in data:
            try:
                comp_id, status = data.split('=')[1].split(',')
                self._state['components'][comp_id] = bool(int(status))
            except (ValueError, KeyError):
                pass
            
        return True

    def close(self):
        """Simulate closing serial connection"""
        self._connected = False
        logger.info("[MOCK] Closed serial connection")