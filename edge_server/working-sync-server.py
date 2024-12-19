from pymodbus.server.sync import StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

import logging
import sys

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName = 'Pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
identity.ProductName = 'Pymodbus Server'
identity.ModelName = 'Pymodbus Server'
identity.MajorMinorRevision = '1.0'

def setup_server():
    # Create datablocks for different register types
    datablock = ModbusSequentialDataBlock(address=6, values=[1]*16)
    inpblock = ModbusSequentialDataBlock(address=3, values=[1]*16)

    # Create a single slave context
    slave_1 = ModbusSlaveContext(
        di=datablock,
        co=datablock,
        hr=datablock,
        ir=inpblock,
    )

    # For a single slave context, just pass the single slave context
    context = ModbusServerContext(slaves=slave_1, single=True)

    # Test reading some values to ensure everything is set up
    print("address: 0x00, value=" + str(context[1].getValues(3, 0)))
    print("address: 0x01, value=" + str(context[1].getValues(3, 1)))

    return context

if __name__ == "__main__":
    ctx = setup_server()
    server = StartSerialServer(
        context=ctx,
        framer=ModbusRtuFramer,
        identity=identity,
        port=sys.argv[1],
        timeout=2,
        baudrate=9600,
        startbit=1,
        databits=1,
        stopbit=2,
        bytesize=8,
        parity='N'
    )