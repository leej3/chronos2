from loguru import logger

class MockSerialHandler:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.state = {
            'status': 'RUNNING',
            'temperature': 22.5
        }
        
    def connect(self):
        logger.info("[MOCK] Connected to serial port")
        return True
            
    def read_data(self):
        return f"STATUS:{self.state['status']};TEMP:{self.state['temperature']}"
            
    def write_data(self, data):
        logger.info(f"[MOCK] Writing data: {data}")
        # Update state based on commands
        if data.startswith(b'TEMP='):
            try:
                self.state['temperature'] = float(data[5:-2])  # Remove TEMP= and \r\n
            except ValueError:
                pass
        return True
            
    def close(self):
        logger.info("[MOCK] Closed serial connection")

class MockModbusHandler:
    def __init__(self, port="/dev/ttyUSB1", baudrate=9600):
        self.state = {
            'chiller_status': 0,
            'boiler_status': 0,
            'temp_sensor_1': 225,  # 22.5°C
            'temp_sensor_2': 235,  # 23.5°C
            'humidity': 450,       # 45.0%
            'system_mode': 0       # OFF
        }
        
    def connect(self):
        logger.info("[MOCK] Connected to Modbus RTU")
        return True
            
    def read_register(self, address, unit=1):
        # Map address to state values
        address_map = {
            0x00: 'chiller_status',
            0x01: 'boiler_status',
            0x02: 'temp_sensor_1',
            0x03: 'temp_sensor_2',
            0x04: 'humidity',
            0x05: 'system_mode'
        }
        if address in address_map:
            return self.state[address_map[address]]
        raise ValueError(f"Invalid register address: {address}")
            
    def write_register(self, address, value, unit=1):
        logger.info(f"[MOCK] Writing value {value} to register {address}")
        # Map address to state values
        address_map = {
            0x00: 'chiller_status',
            0x01: 'boiler_status',
            0x02: 'temp_sensor_1',
            0x03: 'temp_sensor_2',
            0x04: 'humidity',
            0x05: 'system_mode'
        }
        if address in address_map:
            self.state[address_map[address]] = value
            # Update related states based on mode
            if address_map[address] == 'system_mode':
                if value == 1:  # COOLING
                    self.state['chiller_status'] = 1
                    self.state['boiler_status'] = 0
                elif value == 2:  # HEATING
                    self.state['chiller_status'] = 0
                    self.state['boiler_status'] = 1
                else:  # OFF
                    self.state['chiller_status'] = 0
                    self.state['boiler_status'] = 0
        return True
            
    def close(self):
        logger.info("[MOCK] Closed Modbus connection")