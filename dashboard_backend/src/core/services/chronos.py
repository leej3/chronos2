from datetime import UTC, datetime, timedelta

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
        self._devices_chiller = None
        self._devices_boiler = None
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
        #
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.setpoint_repository = SetpointRepository()
        self.edge_server = EdgeServer()

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
        return_temp = self._return_temp or self.get_edge_server_data()["return_temp"]
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
    def mode(self):
        return self.get_edge_server_data()["season_mode"]

    @mode.setter
    def mode(self, mode: str):
        self.setting_repository._update_property_in_db(
            "mode", mode=1 if mode == "summer" else 0
        )

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
    def baseline_setpoint(self):
        wind_chill = int(round(self.outside_temp))
        if wind_chill < 11:
            baseline_setpoint = 100
        else:
            baseline_setpoint = self.setpoint_repository.get_by_value(
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
            temperature_history_adjsutment = self.setpoint_repository.get_by_value(
                "avg_wind_chill", self.wind_chill_avg
            )
        tha_setpoint = self.baseline_setpoint - temperature_history_adjsutment
        if tha_setpoint != self._tha_setpoint:
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
        if Mode.WINTER.value == self.mode:
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        else:
            effective_setpoint = self.tha_setpoint + self.setpoint_offset_summer

        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        if effective_setpoint != self._effective_setpoint:
            self._effective_setpoint = effective_setpoint
        return effective_setpoint

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
                )
                session.add(parameters)

    def get_edge_server_data(self):
        return self.edge_server.get_data()

    def get_state_devices_from_edge_server(self):
        return self.edge_server.get_data()["devices"]

    def boiler_switcher(self):
        if self.is_auto_switch_season:
            if not self.devices_boiler["state"] and self.return_temp <= (
                self.effective_setpoint - self.tolerance
            ):
                self.edge_server.update_device_state(Relay.BOILER.value, True)
            elif self.devices_boiler["state"] and self.return_temp > (
                self.effective_setpoint + self.tolerance
            ):
                self.edge_server.update_device_state(Relay.BOILER.value, False)

    def _find_chiller_index_to_switch(self, status: bool):
        min_date = datetime.now(UTC)
        switch_index = None
        if self.is_auto_switch_season:
            for i, chiller in enumerate(self.devices_chiller[1:], 1):
                if chiller.switched_timestamp < min_date and chiller.state == status:
                    min_date = chiller.switched_timestamp
                switch_index = i
        return switch_index

    def chillers_cascade_switcher(self):
        max_chillers_timestamp = max(
            chiller.switched_timestamp for chiller in self.devices[1:]
        )
        time_gap = (datetime.now(UTC) - max_chillers_timestamp).total_seconds()
        db_delta = self.history_repository.three_minute_avg_delta()
        db_return_temp = self.history_repository.previous_return_temp()

        # Turn on chillers
        if (
            self.return_temp >= (self.effective_setpoint + self.tolerance)
            and db_delta > 0.1
            and time_gap >= self.cascade_time * 60
        ):
            turn_on_index = self._find_chiller_index_to_switch(False)
            try:
                self.edge_server.update_device_state(
                    getattr(Relay, f"CHILLER{turn_on_index}").value, True
                )
            except TypeError:
                pass
        # Turn off chillers
        elif (
            db_return_temp < (self.effective_setpoint - self.tolerance)
            and self.current_delta < 0
            and time_gap >= self.cascade_time * 60 / 1.5
        ):
            turn_off_index = self._find_chiller_index_to_switch(True)
            try:
                self.edge_server.update_device_state(
                    getattr(Relay, f"CHILLER{turn_off_index}").value, False
                )
            except TypeError:
                pass

    def _is_time_to_switch_season_to_summer(self):
        effective_setpoint = self.tha_setpoint + self.setpoint_offset_winter
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        is_switching_season = self.edge_server.get_data()["is_time_to_switch"]
        timespan = datetime.now(UTC) - self.mode_switch_timestamp
        return (
            self.return_temp > (effective_setpoint + self.mode_change_delta_temp)
            and is_switching_season
            and timespan > timedelta(minutes=self.mode_switch_lockout_time)
        )

    def _is_time_to_switch_season_to_winter(self):
        effective_setpoint = self.tha_setpoint + self.setpoint_offset_summer
        effective_setpoint = self._constrain_effective_setpoint(effective_setpoint)
        is_switching_season = self.edge_server.get_data()["is_time_to_switch"]
        timespan = datetime.now(UTC) - self.mode_switch_timestamp
        return (
            self.return_temp < (effective_setpoint - self.mode_change_delta_temp)
            and is_switching_season
            and timespan > timedelta(minutes=self.mode_switch_lockout_time)
        )
