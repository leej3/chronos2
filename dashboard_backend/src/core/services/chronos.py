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
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.boiler import Boiler
from src.core.services.chiller import Chiller
from src.core.services.edge_server import EdgeServer
from src.core.services.valve import Valve
from src.core.utils.constant import (
    EFFICIENCY_HOUR,
    MANUAL_AUTO,
    MANUAL_OFF,
    MANUAL_ON,
    OFF,
    ON,
    WEATHER_HEADERS,
    WEATHER_URL,
    Mode,
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
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        #
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.edge_server = EdgeServer()

    @property
    def mode(self):
        return self.setting_repository._get_property_from_db("mode")

    @mode.setter
    def mode(self, mode: int):
        self.setting_repository._update_property_in_db("mode", mode)

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

    def create_update_history(self):
        edge_server_data = self.edge_server.get_data()
        sensors = edge_server_data["sensors"]
        mode = self.mode
        if mode in (Mode.WINTER.value, Mode.SUMMER.value):
            with session_scope() as session:
                parameters = History(
                    timestamp=get_current_time(UTC),
                    outside_temp=self.outside_temp,
                    water_out_temp=sensors["water_out_temp"],
                    return_temp=sensors["return_temp"],
                    mode=mode,
                )
                session.add(parameters)

    def _switch_devices(self, is_season_switch=False):
        for device in self.devices:
            if device.manual_override == MANUAL_ON:
                device.turn_on(relay_only=True, is_season_switch=is_season_switch)
            elif device.manual_override == MANUAL_OFF:
                device.turn_off(relay_only=True, is_season_switch=is_season_switch)
            elif device.manual_override == MANUAL_AUTO:
                if device.status == ON:
                    device.turn_on(relay_only=True, is_season_switch=is_season_switch)
                elif device.status == OFF:
                    device.turn_off(relay_only=True, is_season_switch=is_season_switch)

    def _save_devices_states(self, mode):
        if mode == Mode.SWITCHING_TO_SUMMER.value:
            self.boiler.save_status()
        elif mode == Mode.SWITCHING_TO_WINTER.value:
            for chiller in self.devices[1:]:
                chiller.save_status()

    def _restore_devices_states(self, mode: Mode):
        if mode == Mode.SWITCHING_TO_SUMMER.value:
            self.boiler.restore_status()
        elif mode == Mode.SWITCHING_TO_WINTER.value:
            for chiller in self.devices[1:]:
                chiller.restore_status()

    def turn_off_devices(
        self, with_valves=False, relay_only=False, is_season_switch=False
    ):
        if relay_only:
            for device in self.devices:
                device.turn_off(
                    relay_only=relay_only, is_season_switch=is_season_switch
                )
        else:
            # for device in self.devices:
            #     device.manual_override = MANUAL_OFF
            if with_valves:
                self.winter_valve.turn_off(is_season_switch=is_season_switch)
                self.summer_valve.turn_off(is_season_switch=is_season_switch)

    def _switch_season(self, mode: int):
        if mode == Mode.WAITING_SWITCH_TO_SUMMER.value:
            logger.debug("Switching to summer mode")
            self.mode = Mode.WAITING_SWITCH_TO_SUMMER.value
            self.mode_switch_timestamp = get_current_time(UTC)
            self._save_devices_states(mode)
            self.turn_off_devices(is_season_switch=True)
            self.summer_valve.turn_on(is_season_switch=True)
            self.winter_valve.turn_off(is_season_switch=True)

            self.scheduler.add_job(
                self._switch_season,
                "date",
                run_date=get_current_time(UTC)
                + timedelta(minutes=self.mode_switch_lockout_time),
                args=[Mode.SWITCHING_TO_SUMMER.value],
            )

        elif mode == Mode.WAITING_SWITCH_TO_WINTER.value:
            logger.debug("Switching to winter mode")
            self.mode = Mode.WAITING_SWITCH_TO_WINTER.value
            self.mode_switch_timestamp = get_current_time(UTC)
            self._save_devices_states(mode)
            self.turn_off_devices(is_season_switch=True)
            self.summer_valve.turn_off(is_season_switch=True)
            self.winter_valve.turn_on(is_season_switch=True)

            self.scheduler.add_job(
                self._switch_season,
                "date",
                run_date=get_current_time(UTC)
                + timedelta(minutes=self.mode_switch_lockout_time),
                args=[Mode.SWITCHING_TO_WINTER.value],
            )

        elif mode == Mode.SWITCHING_TO_WINTER.value:
            logger.debug("Switched to winter mode")
            self._restore_devices_states(mode)
            self._switch_devices(is_season_switch=True)
            self.mode = Mode.WINTER.value

        elif mode == Mode.SWITCHING_TO_SUMMER.value:
            logger.debug("Switched to summer mode")
            self._restore_devices_states(mode)
            self._switch_devices(is_season_switch=True)
            self.mode = Mode.SUMMER.value
