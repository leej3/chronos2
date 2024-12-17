# Component Configuration
COMPONENTS = {
    'CHILLER_1': {'id': 'chiller_1', 'type': 'chiller', 'register': 0x00},
    'CHILLER_2': {'id': 'chiller_2', 'type': 'chiller', 'register': 0x01},
    'CHILLER_3': {'id': 'chiller_3', 'type': 'chiller', 'register': 0x02},
    'CHILLER_4': {'id': 'chiller_4', 'type': 'chiller', 'register': 0x03},
    'BOILER_1': {'id': 'boiler_1', 'type': 'boiler', 'register': 0x04}
}

# Component Groups
COMPONENT_GROUPS = {
    'chillers': ['chiller_1', 'chiller_2', 'chiller_3', 'chiller_4'],
    'boilers': ['boiler_1']
}

# Modbus Register Map
MODBUS_REGISTERS = {
    'COMPONENT_STATUS_BASE': 0x00,  # Status registers start here
    'TEMP_SENSOR_BASE': 0x20,      # Temperature sensor registers start here
    'HUMIDITY': 0x40,
    'SYSTEM_MODE': 0x41
}

# Serial Commands
SERIAL_COMMANDS = {
    'GET_STATUS': 'STATUS\r\n',
    'SET_COOLING': 'MODE=COOL\r\n',
    'SET_HEATING': 'MODE=HEAT\r\n',
    'SET_OFF': 'MODE=OFF\r\n',
    'SET_TEMP': 'TEMP={:.1f}\r\n',
    'SET_COMPONENT': 'COMPONENT={},STATUS={}\r\n'
}

# System Modes
MODES = {
    'COOLING': 1,
    'HEATING': 2,
    'OFF': 0
}

# Temperature limits (°C)
TEMP_LIMITS = {
    'MIN': 16.0,
    'MAX': 30.0
}

# Component Types
COMPONENT_TYPES = {
    'CHILLER': 'chiller',
    'BOILER': 'boiler'
}