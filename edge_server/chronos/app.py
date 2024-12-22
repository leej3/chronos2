import logging
import os
import sys
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import serial
from chronos.config import cfg
from chronos.devices import SerialDevice, safe_read_temperature, ModbusDevice, create_modbus_connection, ModbusException
from chronos.data_models import SystemStatus, DeviceModel, BoilerStats, OperatingStatus, ErrorHistory, SetpointUpdate, ModelInfo
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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
async def get_data():
    """Legacy endpoint for system status."""
    try:
        sensors = {
            "supply": safe_read_temperature(cfg.sensors.in_id),
            "return": safe_read_temperature(cfg.sensors.out_id),
            "outdoor": None  # This sensor is not available in the current config
        }
        devices = {i: DEVICES[i].state for i in range(len(DEVICES))}
        return SystemStatus(sensors=sensors, devices=devices)
    except Exception as e:
        logger.error(f"Error reading data: {e}")
        return SystemStatus(sensors={}, devices={})

@app.get("/device_state", response_model=DeviceModel)
async def get_device_state(device: int = Query(..., ge=0, lt=5, description="The device ID (0-4)")):
    """Legacy endpoint for device state."""
    return DeviceModel(id=device, state=DEVICES[device].state)

@app.post("/device_state")
async def update_device_state(data: DeviceModel):
    """Legacy endpoint for updating device state."""
    device_obj = DEVICES[data.id]
    device_obj.state = data.state
    return DeviceModel(id=device_obj.id, state=device_obj.state)

# New boiler endpoints
@app.get("/boiler/stats", response_model=BoilerStats)
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

@app.get("/download_log")
async def dump_log():
    """Endpoint for downloading log file (not implemented)."""
    raise HTTPException(status_code=501, detail="Not implemented")
  