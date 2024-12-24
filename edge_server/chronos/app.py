import logging
import os
import sys
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Optional, Dict, List, Callable
import asyncio

import serial
from chronos.config import cfg
from chronos.devices import SerialDevice, safe_read_temperature, ModbusDevice, create_modbus_connection, ModbusException
from chronos.data_models import SystemStatus, DeviceModel, BoilerStats, OperatingStatus, ErrorHistory, SetpointUpdate, ModelInfo
from fastapi import FastAPI, Query, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Circuit breaker states and configuration
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.is_open = False

    def record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit breaker opened due to multiple failures")

    def record_success(self):
        """Record a success and reset failure count."""
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if not self.is_open:
            return True
        
        # Check if enough time has passed to try again
        if time.time() - self.last_failure_time >= self.reset_timeout:
            logger.info("Circuit breaker reset timeout reached, allowing retry")
            self.is_open = False
            self.failure_count = 0
            return True
            
        return False

# Rate limiter for temperature changes
class RateLimiter:
    def __init__(self, min_interval: float = 5.0):
        self.min_interval = min_interval
        self.last_change_time = 0

    def can_change(self) -> bool:
        """Check if enough time has passed since last change."""
        current_time = time.time()
        if current_time - self.last_change_time >= self.min_interval:
            self.last_change_time = current_time
            return True
        return False

# Create instances
circuit_breaker = CircuitBreaker()
rate_limiter = RateLimiter()

# Decorator for circuit breaker pattern
def with_circuit_breaker(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not circuit_breaker.can_execute():
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable due to multiple failures. Please try again later."
            )
        
        try:
            result = await func(*args, **kwargs)
            circuit_breaker.record_success()
            return result
        except Exception as e:
            circuit_breaker.record_failure()
            raise
    
    return wrapper

# Decorator for rate limiting
def with_rate_limit(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not rate_limiter.can_change():
            raise HTTPException(
                status_code=429,
                detail="Too many temperature changes. Please wait before trying again."
            )
        return await func(*args, **kwargs)
    
    return wrapper

DeviceTuple = namedtuple(
    "DeviceTuple", ["boiler", "chiller1", "chiller2", "chiller3", "chiller4"]
)

# Initialize devices
DEVICES = DeviceTuple(
    *[SerialDevice(id=i, portname=cfg.serial.portname, baudrate=cfg.serial.baudr) for i in range(5)]
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy endpoints
@app.get("/get_data", response_model=SystemStatus)
@with_circuit_breaker
async def get_data():
    """Legacy endpoint for system status."""
    try:
        sensors = {
            "supply": safe_read_temperature(cfg.sensors.in_id),
            "return": safe_read_temperature(cfg.sensors.out_id),
        }
        devices = {i: DEVICES[i].state for i in range(len(DEVICES))}
        return SystemStatus(sensors=sensors, devices=devices)
    except Exception as e:
        logger.error(f"Error reading data: {e}")
        return SystemStatus(sensors={}, devices={})

@app.get("/device_state", response_model=DeviceModel)
@with_circuit_breaker
async def get_device_state(device: int = Query(..., ge=0, lt=5, description="The device ID (0-4)")):
    """Legacy endpoint for device state."""
    return DeviceModel(id=device, state=DEVICES[device].state)

@app.post("/device_state")
@with_circuit_breaker
@with_rate_limit
async def update_device_state(data: DeviceModel):
    """Legacy endpoint for updating device state."""
    device_obj = DEVICES[data.id]
    device_obj.state = data.state
    return DeviceModel(id=device_obj.id, state=device_obj.state)

# New boiler endpoints
@app.get("/boiler/stats", response_model=BoilerStats)
@with_circuit_breaker
async def get_boiler_stats():
    """Get current boiler statistics."""
    try:
        with create_modbus_connection() as device:
            stats = device.read_boiler_data()
            if not stats:
                raise HTTPException(status_code=500, detail="Failed to read boiler data")
            return BoilerStats(**stats)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read boiler data: {str(e)}")

@app.get("/boiler/status", response_model=OperatingStatus)
@with_circuit_breaker
async def get_boiler_status():
    """Get current boiler operating status."""
    try:
        with create_modbus_connection() as device:
            status = device.read_operating_status()
            if not status:
                raise HTTPException(status_code=500, detail="Failed to read operating status")
            return OperatingStatus(**status)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read operating status: {str(e)}")

@app.get("/boiler/errors", response_model=ErrorHistory)
@with_circuit_breaker
async def get_boiler_errors():
    """Get boiler error history."""
    try:
        with create_modbus_connection() as device:
            history = device.read_error_history()
            if not history:
                history = {
                    "last_lockout_code": None,
                    "last_lockout_str": None,
                    "last_blockout_code": None,
                    "last_blockout_str": None
                }
            return ErrorHistory(**history)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read error history: {str(e)}")

@app.get("/boiler/info", response_model=ModelInfo)
@with_circuit_breaker
async def get_boiler_info():
    """Get boiler model information."""
    try:
        with create_modbus_connection() as device:
            info = device.read_model_info()
            if not info:
                raise HTTPException(status_code=500, detail="Failed to read model info")
            return ModelInfo(**info)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read model info: {str(e)}")

@app.post("/boiler/set_setpoint")
@with_circuit_breaker
@with_rate_limit
async def set_setpoint(data: SetpointUpdate):
    """Update boiler temperature setpoint."""
    try:
        with create_modbus_connection() as device:
            success = device.set_boiler_setpoint(data.temperature)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to set temperature")
            return {"message": f"Temperature setpoint set to {data.temperature}°F"}
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set temperature: {str(e)}")

@app.get("/download_log", response_class=FileResponse)
@with_circuit_breaker
async def download_log():
    """Endpoint for downloading log file"""
    log_path = cfg.files.log_path
    try:
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"File at path {log_path} does not exist.")
        return FileResponse(log_path, media_type="text/plain; charset=utf-8", filename="chronos_log.txt")
    except (FileNotFoundError, RuntimeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5171)
