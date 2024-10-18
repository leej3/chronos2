import serial
from contextlib import contextmanager
from chronos.lib.config_parser import cfg
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient
from chronos.lib.root_logger import root_logger as logger


@contextmanager
def modbus_session():
    modbus = ModbusSerialClient(
        method=cfg.modbus.method,
        baudrate=cfg.modbus.baudr,
        parity=cfg.modbus.parity,
        port=cfg.modbus.portname,
        timeout=cfg.modbus.timeout
    )
    try:
        modbus.connect()
    except (OSError, ModbusException, serial.SerialException) as e:
        logger.error("Unable connect to the boiler via modbus: {}".format(e))
        raise
    else:
        yield modbus
    finally:
        modbus.close()
