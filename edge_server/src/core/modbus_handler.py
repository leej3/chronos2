from pymodbus.client import ModbusSerialClient
from loguru import logger

class ModbusHandler:
    def __init__(self, port="/dev/ttyUSB1", baudrate=9600):
        self.client = ModbusSerialClient(
            method='rtu',
            port=port,
            baudrate=baudrate,
            timeout=1
        )
        
    def connect(self):
        try:
            connected = self.client.connect()
            if connected:
                logger.info("Connected to Modbus RTU")
                return True
            raise Exception("Failed to connect to Modbus")
        except Exception as e:
            logger.error(f"Modbus connection error: {e}")
            raise
            
    def read_register(self, address, unit=1):
        try:
            result = self.client.read_holding_registers(
                address=address,
                count=1,
                unit=unit
            )
            if result.isError():
                raise Exception(f"Modbus read error at address {address}")
            return result.registers[0]
        except Exception as e:
            logger.error(f"Error reading Modbus register: {e}")
            raise
            
    def write_register(self, address, value, unit=1):
        try:
            result = self.client.write_register(
                address=address,
                value=value,
                unit=unit
            )
            if result.isError():
                raise Exception(f"Modbus write error at address {address}")
            return True
        except Exception as e:
            logger.error(f"Error writing to Modbus register: {e}")
            raise
            
    def close(self):
        self.client.close()