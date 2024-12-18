import os
from .lib import db_queries
from .lib.config_parser import cfg
from .lib import Chronos, WINTER, SUMMER, TO_WINTER, TO_SUMMER
from flask import Flask, render_template, Response, jsonify, request, make_response
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
chronos = Chronos()
chronos.scheduler.start()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def get_return_temp():
    read_temp_sensor(cfg.in_id)

def get_water_out_temp():
    read_temp_sensor(cfg.out_id)

def get_data():

    results = {

        "effective_setpoint": get_set_point(),

        "return_temp": get_return_temp(),
        "water_out_temp": get_water_out_temp(),
    }
    # boiler may need get methods for the modbus data and perhaps setpoint
    #  Device class has serial port communication. determine if this is needed.
    #  Remove all db logic. Try to keep the logic for the devices the same.
    actStream = [{
        "timeStamp": device.switched_timestamp.strftime("%B %d, %I:%M %p"),
        "status": device.status,
        "MO": device.manual_override} for device in chronos.devices
    ]
    return {
        "results": results,
        "actStream": actStream,
        "chronos_status": True,
        
    }


@app.route("/download_log")
def dump_log():
    resp = # TODO retrieve
    resp.headers["Content-Disposition"] = "attachment; filename=exported-data.csv"
    return resp


@app.route("/settings", methods=["POST"])
def update_settings():
    for key, value in request.form.items():
        if value:
            setattr(chronos, key, float(value))
    return jsonify(data=request.form)


@app.route("/settings", methods=["GET"])
def update_settings():
    for key, value in request.form.items():
        if value:
            setattr(chronos, key, float(value))
    return jsonify(data=request.form)




@app.route("/")
def index():
    data = get_data()
    return jsonify(data)


@app.route("/state", methods=["POST"])
def update_state():
    device_number = int(request.form["device"])
    manual_override_value = int(request.form["manual_override"])
    chronos.devices[device_number].manual_override = manual_override_value
    return jsonify({"message": "Override updated successfully"})

@app.route("/state", methods=["GET"])
def update_state():
    device_number = int(request.form["device"])
    # TODO: fetch from device and specify a return format
    state = get_state(device_number)
    return jsonify({device_number: state})





if __name__ == "__main__":
    print "App started"
    app.run(host='0.0.0.0', port=5171, debug=True)