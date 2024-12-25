import sys
import threading
import time
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import desc
from sqlalchemy.sql import func
from src.core.chronos.boiler import Boiler
from src.core.chronos.chiller import Chiller
from src.core.chronos.constant import *
from src.core.chronos.valve import Valve
from src.core.configs.database import session_scope
from src.core.configs.root_logger import root_logger as logger
from src.core.models import *
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.utils.config_parser import cfg
from src.core.utils.helpers import c_to_f
from src.core.services.edge_server import EdgeServer


class Chronos(object):

    def __init__(self):
        self.boiler = Boiler()
        self.chiller1 = Chiller(1)
        self.chiller2 = Chiller(2)
        self.chiller3 = Chiller(3)
        self.chiller4 = Chiller(4)
        self.winter_valve = Valve("winter")
        self.summer_valve = Valve("summer")
        self.devices = (
            self.boiler,
            self.chiller1,
            self.chiller2,
            self.chiller3,
            self.chiller4,
        )
        self.valves = (self.winter_valve, self.summer_valve)
        self._outside_temp = None
        self._wind_speed = None
        self._baseline_setpoint = None
        self._tha_setpoint = None
        self._effective_setpoint = None
        self._water_out_temp = None
        self._return_temp = None
        self.scheduler = BackgroundScheduler()
        #
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.edge_server = EdgeServer()

    @staticmethod
    def _read_temperature_sensor(sensor_id):
        # return 50
        device_file = (
            sensor_id  # os.path.join("/sys/bus/w1/devices", sensor_id, "w1_slave")
        )
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
            temp_string = lines[1][equals_pos + 2 :]
            # Divide by 1000 for proper decimal point
            temp = float(temp_string) / 1000.0
            # Convert to degF
            return c_to_f(temp)

    @property
    def water_out_temp(self):
        water_out_temp = self._read_temperature_sensor(cfg.sensors.out_id)
        if water_out_temp != self._water_out_temp:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"water_out_temp": water_out_temp}
            # })
            self._water_out_temp = water_out_temp
        return water_out_temp

    @property
    def return_temp(self):
        return_temp = self._read_temperature_sensor(cfg.sensors.in_id)
        if return_temp != self._return_temp:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"return_temp": return_temp}
            # })
            self._return_temp = return_temp
        return return_temp

    def get_data_from_web(self):
        logger.debug("Retrieve data from web.")
        try:
            # content = urllib2.urlopen(WEATHER_URL, timeout=5)
            data = requests.get(WEATHER_URL, headers=WEATHER_HEADERS).json()
            for zone in data["zones"]:
                for param in zone["parameters"]:
                    if param["name"] == "RAIN":
                        rain_value = param["value"]
                    elif param["name"] == "WIND":
                        wind_speed = float(param["value"])
                    elif param["name"] == "EXT1":
                        outside_temp = round(float(param["value"]), 1)
        except Exception as e:
            logger.error(e)
            logger.error(
                "Unable to get data from the website. Reading previous value from the "
            )
            with session_scope() as session:
                wind_speed, outside_temp = (
                    session.query(History.wind_speed, History.outside_temp)
                    .order_by(desc(History.id))
                    .first()
                )

        if outside_temp != self._outside_temp:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"outside_temp": outside_temp}
            # })
            self._outside_temp = outside_temp
            self._wind_speed = wind_speed
        return {"outside_temp": outside_temp, "wind_speed": wind_speed}

    @property
    def outside_temp(self):
        return self._outside_temp or self.get_data_from_web()["outside_temp"]

    @property
    def wind_speed(self):
        return self._wind_speed or self.get_data_from_web()["wind_speed"]

    def _get_settings_from_db(self, param):
        param = getattr(Settings, param)
        with session_scope() as session:
            (value,) = session.query(param).first()
        return value

    def _update_settings(self, name, value):
        with session_scope() as session:
            property_ = session.query(Settings).first()
            setattr(property_, name, value)
        if name == "cascade_time":
            value /= 60
        if name != "mode_switch_timestamp":
            pass
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {name: value}
            # })

    @property
    def setpoint_offset_summer(self):
        return self._get_settings_from_db("setpoint_offset_summer")

    @setpoint_offset_summer.setter
    def setpoint_offset_summer(self, setpoint_offset):
        self._update_settings("setpoint_offset_summer", setpoint_offset)

    @property
    def setpoint_offset_winter(self):
        return self._get_settings_from_db("setpoint_offset_winter")

    @setpoint_offset_winter.setter
    def setpoint_offset_winter(self, setpoint_offset):
        self._update_settings("setpoint_offset_winter", setpoint_offset)

    @property
    def mode_switch_lockout_time(self):
        return self._get_settings_from_db("mode_switch_lockout_time")

    @mode_switch_lockout_time.setter
    def mode_switch_lockout_time(self, mode_switch_lockout_time):
        self._update_settings("mode_switch_lockout_time", mode_switch_lockout_time)

    @property
    def mode_switch_timestamp(self):
        return self._get_settings_from_db("mode_switch_timestamp")

    @mode_switch_timestamp.setter
    def mode_switch_timestamp(self, mode_switch_timestamp):
        self._update_settings("mode_switch_timestamp", mode_switch_timestamp)

    @property
    def mode(self):
        return self._get_settings_from_db("mode")

    @mode.setter
    def mode(self, mode):
        self._update_settings("mode", mode)

    @property
    def setpoint_min(self):
        return self._get_settings_from_db("setpoint_min")

    @setpoint_min.setter
    def setpoint_min(self, setpoint):
        self._update_settings("setpoint_min", setpoint)

    @property
    def setpoint_max(self):
        return self._get_settings_from_db("setpoint_max")

    @setpoint_max.setter
    def setpoint_max(self, setpoint):
        self._update_settings("setpoint_max", setpoint)

    @property
    def tolerance(self):
        return self._get_settings_from_db("tolerance")

    @tolerance.setter
    def tolerance(self, tolerance):
        self._update_settings("tolerance", tolerance)

    @property
    def cascade_time(self):
        return self._get_settings_from_db("cascade_time") / 60

    @cascade_time.setter
    def cascade_time(self, cascade_time):
        self._update_settings("cascade_time", cascade_time * 60)

    @property
    def mode_change_delta_temp(self):
        return self._get_settings_from_db("mode_change_delta_temp")

    @mode_change_delta_temp.setter
    def mode_change_delta_temp(self, mode_change_delta_temp):
        self._update_settings("mode_change_delta_temp", mode_change_delta_temp)

    @property
    def wind_chill_avg(self):
        with session_scope() as session:
            result = (
                session.query(History.outside_temp)
                .filter(History.timestamp > (datetime.now() - timedelta(days=4)))
                .subquery()
            )
            (wind_chill_avg,) = session.query(func.avg(result.c.outside_temp)).first()
        wind_chill_avg = wind_chill_avg or self.outside_temp
        return int(round(wind_chill_avg))

    @property
    def cascade_fire_rate_avg(self):
        timespan = datetime.now() - timedelta(hours=cfg.efficiency.hours)
        with session_scope() as session:
            result = (
                session.query(History.cascade_fire_rate)
                .order_by(desc(History.id))
                .filter(History.mode == WINTER, History.timestamp > timespan)
                .subquery()
            )
            (average_cascade_fire_rate,) = session.query(
                func.avg(result.c.cascade_fire_rate)
            ).first()
        return average_cascade_fire_rate or 0

    @property
    def baseline_setpoint(self):
        wind_chill = int(round(self.outside_temp))
        if wind_chill < 11:
            baseline_setpoint = 100
        else:
            with session_scope() as session:
                baseline_setpoint = (
                    session.query(SetpointLookup.setpoint)
                    .filter(SetpointLookup.wind_chill == wind_chill)
                    .first()
                )

        if baseline_setpoint != self._baseline_setpoint:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"baseline_setpoint": baseline_setpoint}
            # })
            self._baseline_setpoint = baseline_setpoint
        return baseline_setpoint

    @property
    def tha_setpoint(self):
        if self.wind_chill_avg < 71:
            temperature_history_adjsutment = 0
        else:
            with session_scope() as session:
                (temperature_history_adjsutment,) = (
                    session.query(SetpointLookup.setpoint_offset)
                    .filter(SetpointLookup.avg_wind_chill == self.wind_chill_avg)
                    .first()
                )
        tha_setpoint = self.baseline_setpoint - temperature_history_adjsutment
        if tha_setpoint != self._tha_setpoint:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"tha_setpoint": tha_setpoint}
            # })
            self._tha_setpoint = tha_setpoint
        return tha_setpoint

    def _constrain_effective_setpoint(self, effective_setpoint):
        if effective_setpoint > self.setpoint_max:
            effective_setpoint = self.setpoint_max
        elif effective_setpoint < self.setpoint_min:
            effective_setpoint = self.setpoint_min
        return effective_setpoint

    @property
    def effective_setpoint(self):
        "Calculate setpoint from wind_chill."
        if self.mode in (WINTER, TO_WINTER):
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        elif self.mode in (SUMMER, TO_SUMMER):
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_summer
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        if effective_setpoint != self._effective_setpoint:
            # socketio_client.send({
            #     "event": "misc",
            #     "message": {"effective_setpoint": effective_setpoint}
            # })
            self._effective_setpoint = effective_setpoint
        return effective_setpoint

    def boiler_switcher(self):
        logger.debug("Starting boiler switcher")
        if self.boiler.manual_override == MANUAL_AUTO:
            if (self.boiler.status == OFF and self.return_temp) <= (
                self.effective_setpoint - self.tolerance
            ):
                self.boiler.turn_on()
            elif (self.boiler.status == ON and self.return_temp) > (
                self.effective_setpoint + self.tolerance
            ):
                self.boiler.turn_off()
        logger.debug("Boiler: {}; mode: {}".format(self.boiler.status, self.mode))

    def _find_chiller_index_to_switch(self, status):
        min_date = datetime.now()
        switch_index = None
        for i, chiller in enumerate(self.devices[1:], 1):
            if (
                chiller.timestamp < min_date
                and chiller.manual_override == MANUAL_AUTO
                and chiller.status == status
            ):
                min_date = chiller.timestamp
                switch_index = i
        return switch_index

    @property
    def previous_return_temp(self):
        with session_scope() as session:
            previous_return_temp = (
                session.query(History.return_temp).order_by(desc(History.id)).first()[0]
            )
        return float(previous_return_temp)

    @property
    def current_delta(self):
        current_delta = self.return_temp - self.previous_return_temp
        if current_delta > 0.2:
            current_delta = 1
        elif current_delta < 0:
            current_delta = -1
        else:
            current_delta = 0
        return current_delta

    def chillers_cascade_switcher(self):
        logger.debug("Chiller cascade switcher")
        max_chillers_timestamp = max(
            chiller.switched_timestamp for chiller in self.devices[1:]
        )
        time_gap = (datetime.now() - max_chillers_timestamp).total_seconds()
        db_delta = self.history_repository.three_minute_avg_delta()
        db_return_temp = self.previous_return_temp
        logger.debug(
            ("time_gap: {}; three_minute_avg_delta: {}, last_return_temp: {}").format(
                time_gap, db_delta, db_return_temp
            )
        )
        # Turn on chillers
        if (
            self.return_temp >= (self.effective_setpoint + self.tolerance)
            and db_delta > 0.1
            and time_gap >= self.cascade_time * 60
        ):
            turn_on_index = self._find_chiller_index_to_switch(OFF)
            try:
                self.devices[turn_on_index].turn_on()
            except TypeError:
                pass
        # Turn off chillers
        elif (
            db_return_temp < (self.effective_setpoint - self.tolerance)
            and self.current_delta < 0
            and time_gap >= self.cascade_time * 60 / 1.5
        ):
            turn_off_index = self._find_chiller_index_to_switch(ON)
            try:
                self.devices[turn_off_index].turn_off()
            except TypeError:
                pass

    def _switch_devices(self):
        for device in self.devices:
            if device.manual_override == MANUAL_ON:
                device.turn_on(relay_only=True)
            elif device.manual_override == MANUAL_OFF:
                device.turn_off(relay_only=True)
            elif device.manual_override == MANUAL_AUTO:
                if device.status == ON:
                    device.turn_on(relay_only=True)
                elif device.status == OFF:
                    device.turn_off(relay_only=True)

    def initialize_state(self):
        mode = self.mode
        if mode == WINTER:
            self.winter_valve.turn_on()
            self.summer_valve.turn_off()
            self._switch_devices()
        elif mode == SUMMER:
            self.winter_valve.turn_off()
            self.summer_valve.turn_on()
            self._switch_devices()
        elif mode == TO_SUMMER:
            self.switch_season(FROM_WINTER)
        elif mode == TO_WINTER:
            self.switch_season(FROM_SUMMER)

    def turn_off_devices(self, with_valves=False, relay_only=False):
        if relay_only:
            for device in self.devices:
                device.turn_off(relay_only=relay_only)
        else:
            for device in self.devices:
                device.manual_override = MANUAL_OFF
            if with_valves:
                self.winter_valve.turn_off()
                self.summer_valve.turn_off()

    def update_history(self):
        logger.debug("Updating history")
        mode = self.mode
        if mode in (WINTER, SUMMER):
            with session_scope() as session:
                parameters = History(
                    outside_temp=self.outside_temp,
                    effective_setpoint=self.effective_setpoint,
                    water_out_temp=self.water_out_temp,
                    return_temp=self.return_temp,
                    boiler_status=self.boiler.status,
                    cascade_fire_rate=self.boiler.cascade_current_power,
                    lead_fire_rate=self.boiler.lead_firing_rate,
                    chiller1_status=self.chiller1.status,
                    chiller2_status=self.chiller2.status,
                    chiller3_status=self.chiller3.status,
                    chiller4_status=self.chiller4.status,
                    tha_setpoint=self.tha_setpoint,
                    setpoint_offset_winter=self.setpoint_offset_winter,
                    setpoint_offset_summer=self.setpoint_offset_summer,
                    tolerance=self.tolerance,
                    boiler_manual_override=self.boiler.manual_override,
                    chiller1_manual_override=self.chiller1.manual_override,
                    chiller2_manual_override=self.chiller2.manual_override,
                    chiller3_manual_override=self.chiller3.manual_override,
                    chiller4_manual_override=self.chiller4.manual_override,
                    mode=mode,
                    cascade_time=self.cascade_time,
                    wind_speed=self.wind_speed,
                    avg_outside_temp=self.wind_chill_avg,
                    avg_cascade_fire_rate=self.cascade_fire_rate_avg,
                    delta=self.current_delta,
                )
                session.add(parameters)

    def create_update_history(self):
        logger.debug("Updating history")
        edge_server_data = self.edge_server.get_data()
        sensors = edge_server_data["sensors"]
        mode = self.mode
        if mode in (WINTER, SUMMER):
            with session_scope() as session:
                parameters = History(
                    timestamp=datetime.now(),
                    outside_temp=self.outside_temp,
                    water_out_temp=sensors["water_out_temp"],
                    return_temp=sensors["return_temp"],
                    mode=mode,
                )
                session.add(parameters)

    def switch_season(self, mode):
        if mode == TO_SUMMER:
            logger.debug("Switching to summer mode")
            self.mode = TO_SUMMER
            self._save_devices_states(mode)
            self.turn_off_devices()
            self.summer_valve.turn_on()
            self.winter_valve.turn_off()
            self.scheduler.add_job(
                self.switch_season,
                "date",
                run_date=datetime.now() + timedelta(minutes=VALVES_SWITCH_TIME),
                args=[FROM_WINTER],
            )
        elif mode == TO_WINTER:
            logger.debug("Switching to winter mode")
            self.mode = TO_WINTER
            self._save_devices_states(mode)
            self.turn_off_devices()
            self.summer_valve.turn_off()
            self.winter_valve.turn_on()
            self.scheduler.add_job(
                self.switch_season,
                "date",
                run_date=datetime.now() + timedelta(minutes=VALVES_SWITCH_TIME),
                args=[FROM_SUMMER],
            )
        elif mode == FROM_SUMMER:
            logger.debug("Switched to winter mode")
            self._restore_devices_states(mode)
            self._switch_devices()
            self.mode = WINTER
            self.mode_switch_timestamp = datetime.now()
        elif mode == FROM_WINTER:
            logger.debug("Switched to summer mode")
            self._restore_devices_states(mode)
            self._switch_devices()
            self.mode = SUMMER
            self.mode_switch_timestamp = datetime.now()

    def _save_devices_states(self, mode):
        if mode == TO_SUMMER:
            self.boiler.save_status()
        elif mode == TO_WINTER:
            for chiller in self.devices[1:]:
                chiller.save_status()

    def _restore_devices_states(self, mode):
        if mode == FROM_SUMMER:
            self.boiler.restore_status()
        elif mode == FROM_WINTER:
            for chiller in self.devices[1:]:
                chiller.restore_status()

    @property
    def is_time_to_switch_season_to_summer(self):
        effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        timespan = datetime.now() - self.mode_switch_timestamp
        sum_switch_lockout_time = timedelta(
            minutes=(self.mode_switch_lockout_time + VALVES_SWITCH_TIME)
        )
        return (
            self.return_temp > (effective_setpoint + self.mode_change_delta_temp)
            and timespan > sum_switch_lockout_time
            and
            # this check needs if mode_switch_lockout_time less than 0.
            # https://bitbucket.org/quarck/chronos/issues/37/make-the-chronos-switch-between-season#comment-29724948
            sum_switch_lockout_time > timedelta(minutes=VALVES_SWITCH_TIME)
        )

    @property
    def is_time_to_switch_season_to_winter(self):
        effective_setpoint = self.tha_setpoint + self.setpoint_offset_summer
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        timespan = datetime.now() - self.mode_switch_timestamp
        sum_switch_lockout_time = timedelta(
            minutes=(self.mode_switch_lockout_time + VALVES_SWITCH_TIME)
        )
        return (
            self.return_temp < (effective_setpoint - self.mode_change_delta_temp)
            and timespan > sum_switch_lockout_time
            and sum_switch_lockout_time > timedelta(minutes=VALVES_SWITCH_TIME)
        )

    def emergency_shutdown(self):
        mode = self.mode
        devices = [bool(device.status) for device in self.devices]
        devices_ = zip(self.devices, devices)
        valves = [bool(self.winter_valve.status), bool(self.summer_valve.status)]
        valves_ = zip(self.valves, valves)
        all_devices = devices_ + valves_
        return_temp = self.return_temp
        status_string = "; ".join(
            "{}: {}".format(device[0].table_class_name, device[1])
            for device in all_devices
        )
        shutdown = False
        if all(valves):
            logger.warning(
                "EMERGENCY SHUTDOWN. All valves turned on. Relays states: {}".format(
                    status_string
                )
            )
            self.summer_valve.turn_off()
            self.winter_valve.turn_off()
            shutdown = True
        elif devices[0] and mode == SUMMER:
            logger.warning("EMERGENCY SHUTDOWN. The boiler is turned on in summer mode")
            shutdown = True
        elif any(devices[1:]) and mode == WINTER:
            logger.warning(
                "EMERGENCY SHUTDOWN. One of the chillers is turned on in winter mode. "
                "Relays states: {}".format(status_string)
            )
            shutdown = True
        elif return_temp < 36 or return_temp > 110:
            logger.warning(
                "EMERGENCY SHUTDOWN. The temperature is not in safe range. Temperature: "
                "{}".format(return_temp)
            )
            shutdown = True
        if shutdown:
            self.turn_off_devices()
            threading.interrupt_main()
