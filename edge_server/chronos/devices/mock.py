"""
Mock device implementations for testing and development.
"""

import math
import random
import time
from typing import Any, Dict

from chronos.config import cfg
from chronos.devices.hardware import SerialDevice
from chronos.logging import root_logger as logger


class MockSerialDevice(SerialDevice):
    """
    Mock implementation of SerialDevice.
    Simulates device behavior without requiring actual hardware connections.
    """

    def __init__(
        self, id: int, name: str = None, portname: str = None, baudrate: int = None
    ):
        """Initialize the mock serial device."""
        # Initialize parent with same parameters
        super().__init__(id, portname, baudrate, name)
        self._state = False  # Initial state is OFF
        logger.info(f"Initialized mock serial device {id}")

    def _send_command(self, command: str) -> str:
        """
        Override the _send_command method to simulate responses without
        actually connecting to hardware.
        """
        # Extract the command type and device ID from the command
        parts = command.strip().split()
        if len(parts) < 2:
            return "error"

        if parts[0] == "relay":
            if parts[1] == "read":
                # Return the current state
                return "on" if self._state else "off"
            elif parts[1] == "on":
                # Set state to ON
                self._state = True
                logger.info(f"Set mock device {self._id} to ON")
                return "ok"
            elif parts[1] == "off":
                # Set state to OFF
                self._state = False
                logger.info(f"Set mock device {self._id} to OFF")
                return "ok"

        return "error"


class MockModbusDevice:
    """
    Mock implementation of a Modbus device for testing.
    Simulates boiler behavior without requiring actual hardware connections.
    """

    def __init__(self, port: str = None, baudrate: int = 9600):
        """Initialize the mock Modbus device."""
        # Simulated boiler settings
        self._boiler_setpoint = 140.0
        self._min_setpoint = 120.0
        self._max_setpoint = 180.0

        # Simulated state
        self._operating_mode = 1  # Standby
        self._cascade_mode = 0  # Primary
        self._flame_status = False
        self._pump_status = False

        # For temperature simulation
        self._startup_time = time.time()
        self._current_temp = self._boiler_setpoint - 10.0
        self._last_update_time = time.time()

        logger.info("Initialized mock Modbus device")

    def is_connected(self) -> bool:
        """Always return True for mock device."""
        return True

    def close(self):
        """Simulate closing the connection."""
        pass

    def read_boiler_data(self, max_retries=2) -> Dict[str, Any]:
        """Return simulated boiler data."""
        # Update simulated temperatures
        self._update_simulated_temperatures()

        # Calculate simulated power
        power_pct = 0
        if self._flame_status:
            temp_diff = abs(self._boiler_setpoint - self._current_temp)
            power_pct = min(
                100, max(20, 100 - (temp_diff / self._boiler_setpoint * 100))
            )

        outlet_temp = self._current_temp
        inlet_temp = outlet_temp - 20.0 if self._pump_status else outlet_temp - 5.0

        return {
            "system_supply_temp": self._current_temp,
            "outlet_temp": outlet_temp,
            "inlet_temp": inlet_temp,
            "flue_temp": (
                outlet_temp + 30.0 if self._flame_status else outlet_temp + 5.0
            ),
            "cascade_current_power": power_pct,
            "lead_firing_rate": power_pct,
            "pump_status": self._pump_status,
            "flame_status": self._flame_status,
            "operating_mode": self._operating_mode,
            "operating_mode_str": self._get_operating_mode_str(self._operating_mode),
            "cascade_mode": self._cascade_mode,
            "cascade_mode_str": self._get_cascade_mode_str(self._cascade_mode),
        }

    def read_operating_status(self, max_retries=2) -> Dict[str, Any]:
        """Return simulated operating status."""
        return {
            "operating_mode": self._operating_mode,
            "operating_mode_str": self._get_operating_mode_str(self._operating_mode),
            "cascade_mode": self._cascade_mode,
            "cascade_mode_str": self._get_cascade_mode_str(self._cascade_mode),
            "current_setpoint": self._boiler_setpoint,
            "status": "running" if self._operating_mode in [2, 3, 4] else "standby",
        }

    def set_boiler_setpoint(self, temperature: float, max_retries=2) -> bool:
        """Set the boiler setpoint temperature."""
        # Validate temperature range
        if temperature < cfg.temperature.min_setpoint:
            logger.error(f"Temperature {temperature}°F is below minimum")
            return False
        if temperature > cfg.temperature.max_setpoint:
            logger.error(f"Temperature {temperature}°F is above maximum")
            return False

        self._boiler_setpoint = temperature
        logger.info(f"Set mock boiler setpoint to {temperature}°F")
        return True

    def get_temperature_limits(self, max_retries=2) -> Dict[str, float]:
        """Get the current temperature limits."""
        return {
            "min_setpoint": self._min_setpoint,
            "max_setpoint": self._max_setpoint,
        }

    def set_temperature_limits(
        self, min_setpoint: float, max_setpoint: float, max_retries=2
    ) -> bool:
        """Set the temperature limits."""
        # Validate input ranges
        if (
            min_setpoint < cfg.temperature.min_setpoint
            or max_setpoint > cfg.temperature.max_setpoint
        ):
            return False
        if min_setpoint >= max_setpoint:
            return False

        self._min_setpoint = min_setpoint
        self._max_setpoint = max_setpoint
        logger.info(
            f"Set mock temperature limits: min={min_setpoint}°F, max={max_setpoint}°F"
        )
        return True

    # Helper methods for simulation
    def _update_simulated_temperatures(self):
        """Update the simulated temperatures based on boiler state and setpoint."""
        # Calculate time since last update
        current_time = time.time()
        time_delta = current_time - self._last_update_time
        self._last_update_time = current_time

        # Check if boiler is active
        if self._operating_mode not in [2, 3, 4]:  # Not in heating mode
            # Cool down slowly
            self._current_temp = max(self._current_temp - 0.025 * time_delta, 70.0)
            return

        # If boiler is in heating mode, move toward setpoint
        temp_diff = self._boiler_setpoint - self._current_temp
        if temp_diff > 0:
            # Heat up
            self._current_temp += min(0.05 * time_delta, temp_diff)
        elif temp_diff < 0:
            # Cool down
            self._current_temp += max(-0.05 * time_delta, temp_diff)

    def _simulate_temp(self, base_temp: float, variance: float) -> float:
        """Simulate a temperature with some random variance."""
        time_factor = (time.time() - self._startup_time) / 3600
        wave = math.sin(time_factor * 2 * math.pi)
        noise = random.uniform(-1, 1) * variance * 0.2
        return round(base_temp + wave * variance + noise, 1)

    def _get_operating_mode_str(self, mode: int) -> str:
        """Convert operating mode code to string."""
        modes = {
            0: "Initialization",
            1: "Standby",
            2: "Central Heat",
            3: "Domestic Hot Water",
            4: "Manual",
        }
        return modes.get(mode, "Unknown")

    def _get_cascade_mode_str(self, mode: int) -> str:
        """Convert cascade mode code to string."""
        modes = {
            0: "Primary",
            1: "Secondary",
            2: "Cascade",
        }
        return modes.get(mode, "Unknown")
