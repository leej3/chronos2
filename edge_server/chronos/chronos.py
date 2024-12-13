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


def get_data():
    history, settings = db_queries.get_last_data()
    results = {
        "outside_temp": history.outside_temp,
        "baseline_setpoint": chronos.baseline_setpoint,
        "tha_setpoint": history.tha_setpoint,
        "effective_setpoint": history.effective_setpoint,
        "tolerance": settings.tolerance,
        "setpoint_min": settings.setpoint_min,
        "setpoint_max": settings.setpoint_max,
        "mode_change_delta_temp": settings.mode_change_delta_temp,
        "mode_switch_lockout_time": settings.mode_switch_lockout_time,
        "return_temp": chronos.return_temp,
        "water_out_temp": chronos.water_out_temp,
        "mode": settings.mode,
        "setpoint_offset_summer": settings.setpoint_offset_summer,
        "setpoint_offset_winter": settings.setpoint_offset_winter,
        "cascade_time": settings.cascade_time / 60,
        "wind_chill_avg": history.avg_outside_temp
    }
    efficiency = db_queries.calculate_efficiency()
    efficiency["cascade_fire_rate_avg"] = round(chronos.cascade_fire_rate_avg, 1)
    efficiency["hours"] = cfg.efficiency.hours
    actStream = [{
        "timeStamp": device.switched_timestamp.strftime("%B %d, %I:%M %p"),
        "status": device.status,
        "MO": device.manual_override} for device in chronos.devices
    ]
    return {
        "results": results,
        "actStream": actStream,
        "chronos_status": get_chronos_status(),
        "efficiency": efficiency
    }


def get_chronos_status():
    chronos_status = True
    try:
        with open("/var/run/chronos.pid") as pid_file:
            pid = int(pid_file.readline())
    except IOError:
        chronos_status = False
    else:
        chronos_status = os.path.exists("/proc/{}".format(pid))
    return chronos_status


@app.route("/season_templates")
def get_rendered_season_templates():
    data = get_data()
    return jsonify(data)


@app.route("/download_log")
def dump_log():
    resp = Response(db_queries.log_generator(), mimetype="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=exported-data.csv"
    return resp


@app.route("/update_settings", methods=["POST"])
def update_settings():
    for key, value in request.form.items():
        if value:
            setattr(chronos, key, float(value))
    return jsonify(data=request.form)


@app.route("/switch_mode", methods=["POST"])
def switch_mode():
    mode = int(request.form["mode"])
    if mode == TO_WINTER:
        error = chronos.is_time_to_switch_season_to_summer
        chronos.switch_season(TO_WINTER)
    elif mode == TO_SUMMER:
        error = chronos.is_time_to_switch_season_to_winter
        chronos.switch_season(TO_SUMMER)
    return jsonify(data={
        "error": error,
        "mode_switch_lockout_time": chronos.mode_switch_lockout_time
    })


@app.route("/")
def index():
    data = get_data()
    return jsonify(data)


@app.route("/update_state", methods=["POST"])
def update_state():
    device_number = int(request.form["device"])
    manual_override_value = int(request.form["manual_override"])
    chronos.devices[device_number].manual_override = manual_override_value
    return jsonify({"message": "Override updated successfully"})


@app.route("/winter")
def winter():
    data = get_data()
    return jsonify(data)


@app.route("/summer")
def summer():
    data = get_data()  # Get data from the get_data function
    return jsonify(data)  # Use jsonify to return JSON response


@app.route("/chart_data")
def chart_data():
    data = db_queries.get_chart_data()
    resp = Response(
        response=data,
        status=200,
        mimetype="application/json"
    )
    return resp


if __name__ == "__main__":
    print "App started"
    app.run(host='0.0.0.0', port=5171, debug=True)