import logging
import os
import sys
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import serial
from chronos.config import cfg
from chronos.devices import SerialDevice, read_temperature_sensor, ModbusDevice, create_modbus_connection, ModbusException
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

DeviceTuple = namedtuple(
    "DeviceTuple", ["boiler", "chiller1", "chiller2", "chiller3", "chiller4"]
)

# Legacy models
class SystemStatus(BaseModel):
    sensors: dict
    devices: dict

class DeviceModel(BaseModel):
    id: int
    state: bool

# New models for boiler data
class BoilerStats(BaseModel):
    """Statistics from the boiler including temperatures and performance metrics."""
    system_supply_temp: Optional[float] = Field(None, description="System supply temperature in °F")
    outlet_temp: float = Field(..., description="Outlet temperature in °F")
    inlet_temp: float = Field(..., description="Inlet temperature in °F")
    flue_temp: float = Field(..., description="Flue temperature in °F")
    cascade_current_power: float = Field(..., description="Current cascade power percentage")
    lead_firing_rate: float = Field(..., description="Lead boiler firing rate percentage")
    water_flow_rate: float = Field(..., description="Water flow rate in GPM")
    pump_status: bool = Field(..., description="Pump running status")
    flame_status: bool = Field(..., description="Flame detection status")

class OperatingStatus(BaseModel):
    """Current operating status of the boiler."""
    operating_mode: int = Field(..., description="Current operating mode number")
    operating_mode_str: str = Field(..., description="Operating mode description")
    cascade_mode: int = Field(..., description="Current cascade mode number")
    cascade_mode_str: str = Field(..., description="Cascade mode description")
    current_setpoint: float = Field(..., description="Current temperature setpoint in °F")

class ErrorHistory(BaseModel):
    """Last known error codes from the boiler."""
    last_lockout_code: Optional[int] = Field(None, description="Last lockout error code")
    last_lockout_str: Optional[str] = Field(None, description="Last lockout error description")
    last_blockout_code: Optional[int] = Field(None, description="Last blockout error code")
    last_blockout_str: Optional[str] = Field(None, description="Last blockout error description")

class ModelInfo(BaseModel):
    """Boiler model and version information."""
    model_id: int = Field(..., description="Boiler model ID")
    model_name: str = Field(..., description="Boiler model name")
    firmware_version: str = Field(..., description="Firmware version")
    hardware_version: str = Field(..., description="Hardware version")

class SetpointUpdate(BaseModel):
    """Temperature setpoint update."""
    temperature: float = Field(..., description="Desired temperature setpoint in °F", ge=120, le=180)

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
    sensors = {
        "supply": read_temperature_sensor(cfg.sensors.ids.supply),
        "return": read_temperature_sensor(cfg.sensors.ids.return_),
        "outdoor": read_temperature_sensor(cfg.sensors.ids.outdoor),
    }
    devices = {i: DEVICES[i].state for i in range(len(DEVICES))}
    return SystemStatus(sensors=sensors, devices=devices)

@app.get("/device_state", response_model=DeviceModel)
async def get_device_state(device: int = Query(..., description="The device ID")):
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
            if stats is None:
                raise HTTPException(status_code=500, detail="Failed to read boiler data")
            return BoilerStats(**stats)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/boiler/errors", response_model=ErrorHistory)
async def get_boiler_errors():
    """Get boiler error history."""
    try:
        with create_modbus_connection() as device:
            history = device.read_error_history()
            return ErrorHistory(**history)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/download_log")
async def dump_log():
    raise NotImplementedError("Not implemented")
    return {"message": "Placeholder for downloading log"}
