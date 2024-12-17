from pymodbus.client import ModbusSerialClient
from loguru import logger
from typing import Optional, Dict, Any
from ..config import settings

class ModbusClient:
    def __init__(self):
        self.client = ModbusSerialClient(
            method='rtu',
            port=settings.MODBUS_PORT,
            baudrate=settings.MODBUS_BAUDRATE,
            timeout=1
        )
        self._connected = False

    def connect(self) -> bool:
        """Connect to Modbus RTU"""
        try:
            self._connected = self.client.connect()
            if self._connected:
                logger.info("Connected to Modbus RTU")
                return True
            raise ConnectionError("Failed to connect to Modbus")
        except Exception as e:
            logger.error(f"Modbus connection error: {e}")
            raise

    def read_register(self, address: int, unit: int = 1) -> int:
        """Read value from Modbus register"""
        try:
            if not self._connected:
                self.connect()
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

    def write_register(self, address: int, value: int, unit: int = 1) -> bool:
        """Write value to Modbus register"""
        try:
            if not self._connected:
                self.connect()
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
        """Close Modbus connection"""
        if self._connected:
            self.client.close()
            self._connected = False