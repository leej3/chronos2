import os
from chronos.lib.config_parser import cfg
from chronos.lib.actuators import Boiler, Chiller
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import serial
import time
import sys
from datetime import datetime


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

boiler = Boiler()
chiller1 = Chiller(1)
chiller2 = Chiller(2)
chiller3 = Chiller(3)
chiller4 = Chiller(4)
DEVICES = [boiler, chiller1, chiller2, chiller3, chiller4]

def c_to_f(t):
    return round(((9.0 / 5.0) * t + 32.0), 1)

def _read_temperature_sensor(sensor_id):
        #return 50
        device_file = os.path.join("/sys/bus/w1/devices", sensor_id, "w1_slave")
        while True:
            try:
                with open(device_file) as content:
                    lines = content.readlines()
            except IOError as e:
                logger.error("Temp sensor error: {}".format(e))
                sys.exit(1)
            else:
                if lines[0].strip()[-3:] == "YES":
                    break
                else:
                    time.sleep(0.2)
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            # Divide by 1000 for proper decimal point
            temp = float(temp_string) / 1000.0
            # Convert to degF
            return c_to_f(temp)

def get_return_temp():
    _read_temperature_sensor(cfg.sensors.in_id)

def get_water_out_temp():
    _read_temperature_sensor(cfg.sensors.out_id)

def get_data():

    results = {

        # "effective_setpoint": get_set_point(),

        "return_temp": get_return_temp(),
        "water_out_temp": get_water_out_temp(),
    }
    # boiler may need get methods for the modbus data and perhaps setpoint
    #  Device class has serial port communication. determine if this is needed.
    #  Remove all db logic. Try to keep the logic for the devices the same.
    # TODO: consider instantiating them along with the app

    actStream = [{
        "timeStamp": device.switched_timestamp.strftime("%B %d, %I:%M %p"),
        "status": device.status,
        "MO": device.manual_override} for device in DEVICES
    ]
    return {
        "results": results,
        "actStream": actStream,
        "chronos_status": True,
    }


@app.get("/download_log")
async def dump_log():
    return {"message": "Placeholder for downloading log"}


@app.post("/settings")
async def update_settings(request: Request):
    form_data = await request.form()
    for key, value in form_data.items():
        if value:
            setattr(chronos, key, float(value))
    return {"data": dict(form_data)}

@app.get("/")
async def index():
    data = get_data()
    return data


@app.post("/update_state")
async def update_state(request: Request):
    form_data = await request.form()
    device_number = int(form_data["device"])
    manual_override_value = int(form_data["manual_override"])
    DEVICES[device_number].manual_override = manual_override_value
    return {"message": "Override updated successfully"}






# if __name__ == "__main__":
    # import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5171, debug=True)