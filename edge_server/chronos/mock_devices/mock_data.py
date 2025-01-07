import random

def mock_devices_data():
    return {
        "id": random.randint(0,4),
        "state" : random.choice([True, False])
    }

def mock_boiler_stats():
    return {
        "system_supply_temp": random.uniform(180, 220),  
        "outlet_temp": random.uniform(180, 220),         
        "inlet_temp": random.uniform(160, 200),          
        "flue_temp": random.uniform(300, 400),           
        "cascade_current_power": random.uniform(10, 100),
        "lead_firing_rate": random.uniform(20, 80),    
        "water_flow_rate": random.uniform(10, 50),    
        "pump_status": random.choice([True, False]),     
        "flame_status": random.choice([True, False]),  
    }

def mock_operating_status():
    return {
        "status": random.choice(["running", "idle", "off"]),
        "setpoint_temperature": random.uniform(180, 200), 
        "current_temperature": random.uniform(175, 190),  
        "pressure": random.uniform(1.5, 3.0), 
        "error_code": None if random.choice([True, False]) else random.randint(1000, 9999),  
        "operating_mode": random.randint(1, 5), 
        "operating_mode_str": random.choice(["Heating", "Cooling", "Idle", "Maintenance"]), 
        "cascade_mode": random.randint(1, 3),  
        "cascade_mode_str": random.choice(["Primary", "Secondary", "Tertiary"]), 
        "current_setpoint": random.uniform(180, 200), 
    }

def mock_error_history():
    return {
        "last_lockout_code": random.randint(100, 999) if random.choice([True, False]) else None, 
        "last_lockout_str": random.choice(["Flame Failure", "High Pressure", "Low Water Flow", "Electrical Fault"]) if random.choice([True, False]) else None,
        "last_blockout_code": random.randint(200, 299) if random.choice([True, False]) else None, 
        "last_blockout_str": random.choice(["Low Water Pressure", "Overheating", "System Error", "Pump Failure"]) if random.choice([True, False]) else None,  
    }

def mock_model_info():
    return {
        "model_id": random.randint(1000, 9999),  
        "model_name": random.choice(["CHRONOS-1000", "CHRONOS-2000", "XPERT-3000"]), 
        "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",  
        "hardware_version": f"HW{random.randint(1, 3)}.{random.randint(0, 9)}", 
    }
