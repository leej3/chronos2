import serial
from loguru import logger
from typing import Optional
from ..config import settings

class SerialClient:
    def __init__(self):
        self.port = settings.SERIAL_PORT
        self.baudrate = settings.SERIAL_BAUDRATE
        self.serial = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to serial port"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            self._connected = True
            logger.info(f"Connected to serial port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to serial port: {e}")
            raise

    def read_data(self) -> str:
        """Read data from serial port"""
        if not self._connected:
            self.connect()
        try:
            return self.serial.readline().decode().strip()
        except Exception as e:
            logger.error(f"Error reading from serial: {e}")
            raise

    def write_data(self, data: str) -> bool:
        """Write data to serial port"""
        if not self._connected:
            self.connect()
        try:
            self.serial.write(data.encode())
            return True
        except Exception as e:
            logger.error(f"Error writing to serial: {e}")
            raise

    def close(self):
        """Close serial connection"""
        if self._connected and self.serial:
            self.serial.close()
            self._connected = False