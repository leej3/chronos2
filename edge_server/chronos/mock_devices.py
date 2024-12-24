class MockModbusDevice:
    """Mock Modbus device for testing without hardware."""
    
    def __init__(self, *args, **kwargs):
        self.setpoint = 140  # Default setpoint
        self.is_connected = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read_boiler_data(self):
        """Return mock boiler statistics."""
        return {
            "system_supply_temp": 142.5,  # Optional field
            "outlet_temp": 142.5,
            "inlet_temp": 120.8,
            "flue_temp": 165.3,
            "cascade_current_power": 85.0,
            "lead_firing_rate": 85,
            "water_flow_rate": 45.2,
            "pump_status": True,
            "flame_status": True
        }

    def read_operating_status(self):
        """Return mock operating status."""
        return {
            "operating_mode": 2,  # CH Demand
            "operating_mode_str": "CH Demand",
            "cascade_mode": 0,  # Single Boiler
            "cascade_mode_str": "Single Boiler",
            "current_setpoint": self.setpoint
        }

    def read_error_history(self):
        """Return mock error history."""
        return {
            "last_lockout_code": None,
            "last_lockout_str": None,
            "last_blockout_code": None,
            "last_blockout_str": None
        }

    def read_model_info(self):
        """Return mock model information."""
        return {
            "model_id": 1,  # FTXL 85
            "model_name": "FTXL 85",
            "firmware_version": "2.1.0",
            "hardware_version": "1.0.0"
        }

    def set_boiler_setpoint(self, temperature):
        """Mock setting the boiler temperature."""
        if not (100 <= temperature <= 180):
            return False
        self.setpoint = temperature
        return True 