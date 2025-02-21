#!/usr/bin/env python3
import logging

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


def c_to_f(celsius):
    """Convert Celsius to Fahrenheit."""
    return (9.0 / 5.0) * celsius + 32.0


class BoilerReader:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, parity="E", timeout=1):
        """Initialize Modbus client for boiler communication.

        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0' for Linux, 'COM1' for Windows)
            baudrate (int): Baud rate (typically 9600)
            parity (str): Parity ('N' for none, 'E' for even, 'O' for odd)
            timeout (int): Communication timeout in seconds
        """
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            timeout=timeout,
        )
        self.client.unit = 1  # Set Modbus unit ID after client creation

        # Operating modes
        self.operating_modes = {
            "0": "Initialization",
            "1": "Standby",
            "2": "CH Demand",  # Central Heat Demand
            "3": "DHW Demand",  # Domestic Hot Water Demand
            "4": "CH & DHW Demand",
            "5": "Manual Operation",
            "6": "Shutdown",
            "7": "Error",
            "8": "Manual Operation 2",
            "9": "Freeze Protection",
            "10": "Sensor Test",
        }

        # Cascade modes
        self.cascade_modes = {"0": "Single Boiler", "1": "Manager", "2": "Member"}

    def connect(self):
        """Connect to the boiler."""
        if not self.client.connect():
            raise ConnectionError("Failed to connect to boiler")
        logger.info("Successfully connected to boiler")

    def close(self):
        """Close the connection."""
        self.client.close()
        logger.info("Connection closed")

    def read_register(self, address, count=1):
        """Read holding register(s).

        Args:
            address (int): Register address (0-based)
            count (int): Number of registers to read

        Returns:
            list: Register values
        """
        try:
            # Note: address is passed as a keyword argument
            result = self.client.read_holding_registers(address=address, count=count)
            if result.isError():
                raise ModbusException(f"Error reading register {address}")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read register {address}: {e}")
            return None

    def read_input_register(self, address, count=1):
        """Read input register(s).

        Args:
            address (int): Register address (0-based)
            count (int): Number of registers to read

        Returns:
            list: Register values
        """
        try:
            # Note: address is passed as a keyword argument
            result = self.client.read_input_registers(address=address, count=count)
            if result.isError():
                raise ModbusException(f"Error reading input register {address}")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read input register {address}: {e}")
            return None

    def get_boiler_info(self):
        """Read all available boiler information.

        This implementation has been verified against the working C implementation (bstat).
        Register readings fall into these categories:

        Verified Working (matching bstat):
        - Temperatures (all converted from C to F, divided by 10):
            - System Supply Temp (40006)
            - Outlet Temp (30008)
            - Inlet Temp (30009)
            - Flue Temp (30010)
        - Performance:
            - Cascade Current Power (30006) - direct percentage
            - Lead Firing Rate (30011) - direct percentage
        - Status:
            - Operating Mode (40001) - with string mapping
            - Cascade Mode (40002) - with string mapping
            - Alarm/Pump/Flame Status (30003-30005) - boolean values

        Unverified/Potentially Incorrect:
        - Setpoints (40003-40005):
            Note: The working implementation reads setpoint from a file rather than Modbus.
            These values may not be accurate or may need different scaling.

        Returns:
            dict: Dictionary containing boiler statistics, or None if read failed
        """
        try:
            info = {}

            # Read holding registers block (operating mode through supply temp)
            h_result = self.read_register(0, count=7)  # Read registers 40001-40007
            if h_result:
                info.update(
                    {
                        # System Status - Verified working
                        "Operating Mode": h_result[0],
                        "Operating Mode String": self.operating_modes.get(
                            str(h_result[0]), f"Unknown ({h_result[0]})"
                        ),
                        "Cascade Mode": h_result[1],
                        "Cascade Mode String": self.cascade_modes.get(
                            str(h_result[1]), f"Unknown ({h_result[1]})"
                        ),
                        # Setpoints - Unverified, may be incorrect
                        "Current Setpoint": round(c_to_f(h_result[2] / 10.0), 1),
                        "Min Setpoint": round(c_to_f(h_result[3] / 10.0), 1),
                        "Max Setpoint": round(c_to_f(h_result[4] / 10.0), 1),
                        # Temperature - Verified working
                        "System Supply Temp": (
                            round(c_to_f(h_result[6] / 10.0), 1)
                            if h_result[6] != 0
                            else 0
                        ),
                    }
                )

            # Read input registers block (status through firing rate)
            i_result = self.read_input_register(
                3, count=9
            )  # Read registers 30003-30011
            if i_result:
                info.update(
                    {
                        # Status Flags - Verified working
                        "Alarm Status": bool(i_result[0]),
                        "Pump Status": bool(i_result[1]),
                        "Flame Status": bool(i_result[2]),
                        # Performance - Verified working
                        "Cascade Current Power": float(i_result[3]),
                        # Temperatures - Verified working
                        "Outlet Temp": round(c_to_f(i_result[5] / 10.0), 1),
                        "Inlet Temp": round(c_to_f(i_result[6] / 10.0), 1),
                        "Flue Temp": round(c_to_f(i_result[7] / 10.0), 1),
                        "Lead Firing Rate": float(i_result[8]),
                    }
                )

            return info

        except Exception as e:
            logger.error(f"Error getting boiler info: {e}")
            return None


def main():
    reader = None  # Initialize reader to None
    try:
        # Create reader instance - adjust parameters for your setup
        reader = BoilerReader(
            port="/dev/ttyUSB0",  # Adjust this to match your system
            baudrate=9600,
            parity="E",
            timeout=1,
        )

        # Connect to boiler
        reader.connect()

        # Read boiler information
        info = reader.get_boiler_info()

        if info:
            print("\nBoiler Information:")
            print("=" * 50)

            # System Status
            print("\nSystem Status:")
            print("-" * 20)
            print(
                f"Operating Mode: {info.get('Operating Mode', 'N/A')} ({info.get('Operating Mode String', 'N/A')})"
            )
            print(
                f"Cascade Mode: {info.get('Cascade Mode', 'N/A')} ({info.get('Cascade Mode String', 'N/A')})"
            )

            # Setpoints
            print("\nSetpoints:")
            print("-" * 20)
            print(f"Current Setpoint: {info.get('Current Setpoint', 'N/A')}°F")
            print(f"Min Setpoint: {info.get('Min Setpoint', 'N/A')}°F")
            print(f"Max Setpoint: {info.get('Max Setpoint', 'N/A')}°F")

            # Temperatures
            print("\nTemperatures:")
            print("-" * 20)
            print(f"System Supply Temp: {info.get('System Supply Temp', 'N/A')}°F")
            print(f"Outlet Temp: {info.get('Outlet Temp', 'N/A')}°F")
            print(f"Inlet Temp: {info.get('Inlet Temp', 'N/A')}°F")
            print(f"Flue Temp: {info.get('Flue Temp', 'N/A')}°F")

            # Status Flags
            print("\nStatus Flags:")
            print("-" * 20)
            print(f"Alarm Status: {info.get('Alarm Status', 'N/A')}")
            print(f"Pump Status: {info.get('Pump Status', 'N/A')}")
            print(f"Flame Status: {info.get('Flame Status', 'N/A')}")

            # Performance
            print("\nPerformance:")
            print("-" * 20)
            print(f"Cascade Current Power: {info.get('Cascade Current Power', 'N/A')}%")
            print(f"Lead Firing Rate: {info.get('Lead Firing Rate', 'N/A')}%")

            # Visual Representation
            print("\nVisual:")
            print("-" * 20)
            print("    +-------------+")
            print(
                f"    |             | {info.get('Outlet Temp', 'N/A')}°F              {info.get('System Supply Temp', 'N/A')}°F"
            )
            print("    |Cascade Fire |---------------------------->")
            print(f"    |    {info.get('Cascade Current Power', 0):.0f}%      |")
            print("    |             |")
            print("    | Lead Fire   |")
            print(f"    |    {info.get('Lead Firing Rate', 0):.0f}%     |")
            print(f"    |             |  {info.get('Inlet Temp', 'N/A')}°F")
            print("    |             |<----------------------------")
            print("    +-------------+")

        else:
            print("Failed to read boiler information")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        if reader:  # Only close if reader was successfully created
            reader.close()


if __name__ == "__main__":
    main()
