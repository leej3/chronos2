import logging
import os
import sys
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import serial
from chronos.lib.config import cfg
from chronos.lib.devices import SerialDevice, read_temperature_sensor
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

DeviceTuple = namedtuple(
    "DeviceTuple", ["boiler", "chiller1", "chiller2", "chiller3", "chiller4"]
)
DEVICES = DeviceTuple(*[SerialDevice(i) for i in range(5)])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeviceModel(BaseModel):
    id: int
    state: bool


class SystemStatus(BaseModel):
    sensors: dict[str, float]
    devices: list[DeviceModel]


@app.get("/", response_model=SystemStatus)
async def get_data():
    sensors = {
        "return_temp": read_temperature_sensor(cfg.sensors.in_id),
        "water_out_temp": read_temperature_sensor(cfg.sensors.out_id),
    }
    devices = [DeviceModel(id=device.id, state=device.state) for device in DEVICES]
    return SystemStatus(sensors=sensors, devices=devices)


@app.get("/device_state", response_model=DeviceModel)
async def get_device_state(device: int = Query(..., description="The device ID")):
    return DeviceModel(id=device, state=DEVICES[device].state)


@app.post("/device_state")
async def update_device_state(data: DeviceModel):
    device_obj = DEVICES[data.id]
    device_obj.state = data.state
    return DeviceModel(id=device_obj.id, state=device_obj.state)


@app.get("/download_log")
async def dump_log():
    raise NotImplementedError("Not implemented")
    return {"message": "Placeholder for downloading log"}
