from datetime import UTC, datetime, timedelta, timezone

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import desc
from sqlalchemy.sql import func
from src.core.configs.database import session_scope
from src.core.configs.root_logger import root_logger as logger
from src.core.models import History
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setpoint_repository import SetpointRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.boiler import Boiler
from src.core.services.chiller import Chiller
from src.core.services.edge_server import EdgeServer
from src.core.services.valve import Valve
from src.core.utils.constant import (
    EFFICIENCY_HOUR,
    WEATHER_HEADERS,
    WEATHER_URL,
    Mode,
    Relay,
)
from src.core.utils.helpers import get_current_time

scheduler = AsyncIOScheduler()


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
        self._setpoint_min = None
        self._setpoint_max = None
        self._is_auto_switch_season = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.device_map = {
            Relay.BOILER.value: self.boiler,
            Relay.CHILLER1.value: self.chiller1,
            Relay.CHILLER2.value: self.chiller2,
            Relay.CHILLER3.value: self.chiller3,
            Relay.CHILLER4.value: self.chiller4,
        }
        #
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.setpoint_repository = SetpointRepository()
        self.edge_server = EdgeServer()

    @property
    def is_auto_switch_season(self):
        is_auto_switch_season = self.setting_repository._get_property_from_db(
            "is_auto_switch_season"
        )
        if is_auto_switch_season != self._is_auto_switch_season:
            self._is_auto_switch_season = is_auto_switch_season
        return is_auto_switch_season

    @is_auto_switch_season.setter
    def is_auto_switch_season(self, is_auto_switch_season):
        self.setting_repository._update_property_in_db(
            "is_auto_switch_season", is_auto_switch_season
        )

    @property
    def setpoint_offset_summer(self):
        return self.setting_repository._get_property_from_db("setpoint_offset_summer")

    @setpoint_offset_summer.setter
    def setpoint_offset_summer(self, setpoint_offset):
        self.setting_repository._update_property_in_db(
            "setpoint_offset_summer", setpoint_offset
        )

    @property
    def setpoint_offset_winter(self):
        return self.setting_repository._get_property_from_db("setpoint_offset_winter")

    @setpoint_offset_winter.setter
    def setpoint_offset_winter(self, setpoint_offset):
        self.setting_repository._update_property_in_db(
            "setpoint_offset_winter", setpoint_offset
        )

    @property
    def devices_chiller(self):
        devices = self.get_state_devices_from_edge_server()
        self._devices_chiller = (
            devices[Relay.CHILLER1.value],
            devices[Relay.CHILLER2.value],
            devices[Relay.CHILLER3.value],
            devices[Relay.CHILLER4.value],
        )
        return self._devices_chiller

    @property
    def devices_boiler(self):
        devices = self.get_state_devices_from_edge_server()
        self._devices_boiler = devices[Relay.BOILER.value]
        return self._devices_boiler

    @property
    def is_auto_switch_season(self):
        return (
            self._is_auto_switch_season
            or self.setting_repository._get_property_from_db("is_auto_switch_season")
        )

    @is_auto_switch_season.setter
    def is_auto_switch_season(self, is_auto_switch_season):
        self.setting_repository._update_property_in_db(
            "is_auto_switch_season", is_auto_switch_season
        )

    @property
    def return_temp(self):
        sensors = self.get_edge_server_data()["sensors"]
        return_temp = self._return_temp or sensors["return_temp"]
        if return_temp != self._return_temp:
            self._return_temp = return_temp
        return return_temp

    @property
    def tolerance(self):
        return self.setting_repository._get_property_from_db("tolerance")

    @tolerance.setter
    def tolerance(self, tolerance):
        self.setting_repository._update_property_in_db("tolerance", tolerance)

    @property
    def mode_change_delta_temp(self):
        return self.setting_repository._get_property_from_db("mode_change_delta_temp")

    @mode_change_delta_temp.setter
    def mode_change_delta_temp(self, mode_change_delta_temp):
        self.setting_repository._update_property_in_db(
            "mode_change_delta_temp", mode_change_delta_temp
        )

    @property
    def mode(self):
        return self.get_edge_server_data()["season_mode"]

    @mode.setter
    def mode(self, mode: str):
        mode_value = 1 if mode == "summer" else 0
        self.setting_repository._update_property_in_db("mode", mode_value)

    def get_data_from_web(self):
        logger.debug("Retrieve data from web.")
        try:
            # content = urllib2.urlopen(WEATHER_URL, timeout=5)
            data = requests.get(WEATHER_URL, headers=WEATHER_HEADERS).json()
            for zone in data["zones"]:
                for param in zone["parameters"]:
                    if param["name"] == "RAIN":
                        _ = param["value"]  # Collect but currently unused
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
            self._outside_temp = outside_temp
            self._wind_speed = wind_speed
        return {"outside_temp": outside_temp, "wind_speed": wind_speed}

    @property
    def outside_temp(self):
        return self._outside_temp or self.get_data_from_web()["outside_temp"]

    @property
    def wind_speed(self):
        return self._wind_speed or self.get_data_from_web()["wind_speed"]

    @property
    def setpoint_min(self):
        return self._setpoint_min or self.setting_repository._get_property_from_db(
            "setpoint_min"
        )

    @setpoint_min.setter
    def setpoint_min(self, setpoint_min):
        self.setting_repository._update_property_in_db("setpoint_min", setpoint_min)

    @property
    def setpoint_max(self):
        return self._setpoint_max or self.setting_repository._get_property_from_db(
            "setpoint_max"
        )

    @setpoint_max.setter
    def setpoint_max(self, setpoint_max):
        self.setting_repository._update_property_in_db("setpoint_max", setpoint_max)

    @property
    def cascade_fire_rate_avg(self):
        timespan = datetime.now() - timedelta(hours=EFFICIENCY_HOUR)
        with session_scope() as session:
            result = (
                session.query(History.cascade_fire_rate)
                .order_by(desc(History.id))
                .filter(History.mode == Mode.WINTER.value, History.timestamp > timespan)
                .subquery()
            )
            (average_cascade_fire_rate,) = session.query(
                func.avg(result.c.cascade_fire_rate)
            ).first()
        return average_cascade_fire_rate or 0

    @property
    def mode_switch_lockout_time(self):
        return self.setting_repository._get_property_from_db("mode_switch_lockout_time")

    @mode_switch_lockout_time.setter
    def mode_switch_lockout_time(self, mode_switch_lockout_time):
        self.setting_repository._update_property_in_db(
            "mode_switch_lockout_time", mode_switch_lockout_time
        )

    @property
    def mode_switch_timestamp(self):
        return self.setting_repository._get_property_from_db("mode_switch_timestamp")

    @mode_switch_timestamp.setter
    def mode_switch_timestamp(self, mode_switch_timestamp):
        self.setting_repository._update_property_in_db(
            "mode_switch_timestamp", mode_switch_timestamp
        )

    @property
    def wind_chill_avg(self):
        return self.history_repository.wind_chill_avg()

    @property
    def baseline_setpoint(self):
        wind_chill = int(round(self.outside_temp))
        if wind_chill < 11:
            baseline_setpoint = 100
        else:
            baseline_setpoint = self.setpoint_repository.get_setpoint_by_param_value(
                "wind_chill", wind_chill
            )

        if baseline_setpoint != self._baseline_setpoint:
            self._baseline_setpoint = baseline_setpoint
        return baseline_setpoint

    @property
    def tha_setpoint(self):
        if self.wind_chill_avg < 71:
            temperature_history_adjsutment = 0
        else:
            temperature_history_adjsutment = (
                self.setpoint_repository.get_setpoint_by_param_value(
                    "avg_wind_chill", self.wind_chill_avg
                )
            )
        tha_setpoint = self.baseline_setpoint - temperature_history_adjsutment
        if tha_setpoint != self._tha_setpoint:
            self._tha_setpoint = tha_setpoint
        return tha_setpoint

    @property
    def cascade_time(self):
        return self.setting_repository._get_property_from_db("cascade_time") / 60

    @cascade_time.setter
    def cascade_time(self, cascade_time):
        self.setting_repository._update_property_in_db(
            "cascade_time", cascade_time * 60
        )

    def _constrain_effective_setpoint(self, effective_setpoint):
        if effective_setpoint > self.setpoint_max:
            effective_setpoint = self.setpoint_max
        elif effective_setpoint < self.setpoint_min:
            effective_setpoint = self.setpoint_min
        return effective_setpoint

    @property
    def effective_setpoint(self):
        if Mode.WINTER.value == self.mode:
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        else:
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_summer

        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        if effective_setpoint != self._effective_setpoint:
            self._effective_setpoint = effective_setpoint
        return effective_setpoint

    @property
    def previous_return_temp(self):
        return self.history_repository.previous_return_temp()

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

    def create_update_history(self):
        edge_server_data = self.get_edge_server_data()
        sensors = edge_server_data["sensors"]
        mode = self.mode
        if mode in ("winter", "summer"):
            with session_scope() as session:
                parameters = History(
                    timestamp=get_current_time(UTC),
                    outside_temp=self.outside_temp,
                    water_out_temp=sensors["water_out_temp"],
                    return_temp=sensors["return_temp"],
                    mode=0 if mode == "winter" else 1,
                    tha_setpoint=self.tha_setpoint,
                    setpoint_offset_winter=self.setpoint_offset_winter,
                    setpoint_offset_summer=self.setpoint_offset_summer,
                    tolerance=self.tolerance,
                    cascade_time=self.cascade_time,
                    wind_speed=self.wind_speed,
                    avg_outside_temp=self.wind_chill_avg,
                    avg_cascade_fire_rate=self.cascade_fire_rate_avg,
                    delta=self.current_delta,
                )
                session.add(parameters)

    def get_edge_server_data(self):
        return self.edge_server.get_data()

    def get_state_devices_from_edge_server(self):
        return self.edge_server.get_state_of_all_relays()

    def boiler_switcher(
        self, devices_boiler, return_temp, effective_setpoint, tolerance
    ):
        if not devices_boiler["state"] and return_temp <= (
            effective_setpoint - tolerance
        ):
            self.edge_server.update_device_state(Relay.BOILER.value, True)
        elif devices_boiler["state"] and return_temp > (effective_setpoint + tolerance):
            self.edge_server.update_device_state(Relay.BOILER.value, False)

    def _find_chiller_index_to_switch(self, status: bool, devices_chiller):
        min_date = datetime.now(UTC)
        switch_index = None
        for i, chiller in enumerate(devices_chiller[1:], 1):
            if chiller["switched_timestamp"] < min_date and chiller["state"] == status:
                min_date = chiller["switched_timestamp"]
                switch_index = i
        return switch_index

    def chillers_cascade_switcher(
        self,
        return_temp,
        devices_boiler,
        devices_chiller,
        effective_setpoint,
        mode_change_delta_temp,
        tolerance,
    ):
        # Find the most recently switched chiller timestamp
        max_chillers_timestamp = max(
            chiller["switched_timestamp"] for chiller in devices_chiller[1:]
        )

        max_chillers_timestamp = (
            datetime.strptime(max_chillers_timestamp, "%Y-%m-%dT%H:%M:%SZ")
            if isinstance(max_chillers_timestamp, str)
            else max_chillers_timestamp
        ).replace(tzinfo=timezone.utc)

        time_gap = (datetime.now(timezone.utc) - max_chillers_timestamp).total_seconds()

        db_delta = self.history_repository.three_minute_avg_delta()
        db_return_temp = self.history_repository.previous_return_temp()
        # Turn on chillers
        if (
            return_temp >= (effective_setpoint + tolerance)
            and db_delta > 0.1
            and time_gap >= self.cascade_time * 60
        ):
            turn_on_index = self._find_chiller_index_to_switch(False, devices_chiller)
            try:
                self.edge_server.update_device_state(
                    getattr(Relay, f"CHILLER{turn_on_index}").value, True
                )
            except TypeError:
                pass
        # Turn off chillers
        elif (
            db_return_temp < (effective_setpoint - tolerance)
            and self.current_delta < 0
            and time_gap >= self.cascade_time * 60 / 1.5
        ):
            turn_off_index = self._find_chiller_index_to_switch(True, devices_chiller)
            try:
                self.edge_server.update_device_state(
                    getattr(Relay, f"CHILLER{turn_off_index}").value, False
                )
            except TypeError:
                pass

    def _get_data_auto_switch(self):
        data = self.edge_server.get_data()
        tolerance = self.tolerance
        is_switching_season = data["is_switching_season"]
        return_temp = data["sensors"]["return_temp"]
        mode_change_delta_temp = self.mode_change_delta_temp
        devices = self.get_state_devices_from_edge_server()
        for i in range(len(devices)):
            devices[i]["switched_timestamp"] = self._get_switch_timestamp(
                devices[i]["id"]
            )

        devices_boiler = devices[Relay.BOILER.value]
        devices_chiller = (
            devices[Relay.CHILLER1.value],
            devices[Relay.CHILLER2.value],
            devices[Relay.CHILLER3.value],
            devices[Relay.CHILLER4.value],
        )
        effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)

        return (
            is_switching_season,
            return_temp,
            mode_change_delta_temp,
            devices_boiler,
            devices_chiller,
            tolerance,
            effective_setpoint,
        )

    def _is_time_to_switch_season_to_summer(self):
        (
            is_switching_season,
            return_temp,
            mode_change_delta_temp,
            devices_boiler,
            devices_chiller,
            tolerance,
            effective_setpoint,
        ) = self._get_data_auto_switch()

        self.boiler_switcher(devices_boiler, return_temp, effective_setpoint, tolerance)
        return (
            return_temp > (effective_setpoint + mode_change_delta_temp)
            and not is_switching_season
        )

    def _is_time_to_switch_season_to_winter(self):
        (
            is_switching_season,
            return_temp,
            mode_change_delta_temp,
            devices_boiler,
            devices_chiller,
            tolerance,
            effective_setpoint,
        ) = self._get_data_auto_switch()

        self.chillers_cascade_switcher(
            return_temp,
            devices_boiler,
            devices_chiller,
            effective_setpoint,
            mode_change_delta_temp,
            tolerance,
        )

        return (
            return_temp < (effective_setpoint - mode_change_delta_temp)
            and not is_switching_season
        )

    def _turn_off_all_devices(self):
        self.edge_server.turn_off_all_devices()

    async def _switch_season_auto(self):
        current_mode = self.mode
        if current_mode == "winter":
            if self._is_time_to_switch_season_to_summer():
                self.edge_server.season_switch("summer", self.mode_switch_lockout_time)
        elif current_mode == "summer":
            if self._is_time_to_switch_season_to_winter():
                self.edge_server.season_switch("winter", self.mode_switch_lockout_time)

    def _get_device(self, id: int):
        return self.device_map.get(id)

    def _get_switch_timestamp(self, id: int):
        device = self._get_device(id)
        return device.switched_timestamp if device else None
