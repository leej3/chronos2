import pytest
from unittest.mock import patch, MagicMock
from chronos.lib.devices import ModbusDevice
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@patch("chronos.lib.devices.ModbusSerialClient")
def test_modbus_device_init(mock_modbus_client):
    logger.debug("Starting test_modbus_device_init")
    mock_instance = MagicMock()
    mock_modbus_client.return_value = mock_instance
    device = ModbusDevice(port="/dev/ttyUSB0", baudrate=9600, parity='E')
    logger.debug("ModbusDevice initialized")
    
    # The mocked client constructor was called
    mock_modbus_client.assert_called_with(
        port="/dev/ttyUSB0",
        baudrate=9600,
        parity='E',
        timeout=1
    )

    # Example: test read_coil call
    mock_instance.read_coils.return_value.isError.return_value = False
    mock_instance.read_coils.return_value.bits = [1]  # coil is True
    read_val = device.read_coil(10, unit=1)
    logger.debug(f"Read coil value: {read_val}")
    assert read_val is True


    # Example: test set_coil call
    mock_instance.write_coil.return_value.isError.return_value = False
    success = device.set_coil(10, True, unit=1)
    logger.debug(f"Set coil success: {success}")
    assert success is True

    # Cleanup
    device.close()
    mock_instance.close.assert_called_once()
    logger.debug("Finished test_modbus_device_init")