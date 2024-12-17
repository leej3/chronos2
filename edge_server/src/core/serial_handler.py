import serial
from loguru import logger

class SerialHandler:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
    def connect(self):
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            logger.info(f"Connected to serial port {self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to serial port: {e}")
            raise
            
    def read_data(self):
        if not self.serial:
            self.connect()
        try:
            return self.serial.readline().decode().strip()
        except Exception as e:
            logger.error(f"Error reading from serial: {e}")
            raise
            
    def write_data(self, data):
        if not self.serial:
            self.connect()
        try:
            self.serial.write(data.encode())
            return True
        except Exception as e:
            logger.error(f"Error writing to serial: {e}")
            raise
            
    def close(self):
        if self.serial:
            self.serial.close()