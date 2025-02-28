from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.sql import func
from src.core.configs.database import session_scope
from src.core.models import History
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.core.utils.constant import EFFICIENCY_HOUR, Mode, Relay, State
from src.core.utils.helpers import convert_datetime_to_str, get_current_time


class DashboardService:
    def __init__(self):
        self.chronos = Chronos()
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()
        self.edge_server = EdgeServer()
        self.device_map = {
            Relay.BOILER.value: self.chronos.boiler,
            Relay.CHILLER1.value: self.chronos.chiller1,
            Relay.CHILLER2.value: self.chronos.chiller2,
            Relay.CHILLER3.value: self.chronos.chiller3,
            Relay.CHILLER4.value: self.chronos.chiller4,
        }

    def _get_device(self, id: int):
        return self.device_map.get(id)

    def get_data(self):
        history = self.history_repository.get_last_history()
        settings = self.setting_repository.get_last_settings()

        edge_server_data = self.edge_server.get_data()
        devices = self.edge_server.get_state_of_all_relays()
        for i in range(len(devices)):
            devices[i]["switched_timestamp"] = convert_datetime_to_str(
                self.get_switch_timestamp(devices[i]["id"]), "%Y-%m-%dT%H:%M:%SZ"
            )

        results = {
            "outside_temp": getattr(history, "outside_temp", 0),
            "baseline_setpoint": getattr(self.chronos, "baseline_setpoint", 0),
            "tha_setpoint": getattr(history, "tha_setpoint", 0),
            "effective_setpoint": getattr(history, "effective_setpoint", 0),
            "tolerance": getattr(settings, "tolerance", 0),
            "setpoint_min": getattr(settings, "setpoint_min", 0),
            "setpoint_max": getattr(settings, "setpoint_max", 0),
            "mode_change_delta_temp": getattr(settings, "mode_change_delta_temp", 0),
            "mode_switch_lockout_time": getattr(
                settings, "mode_switch_lockout_time", 0
            ),
            "mode": getattr(settings, "mode", 0),
            "setpoint_offset_summer": getattr(settings, "setpoint_offset_summer", 0),
            "setpoint_offset_winter": getattr(settings, "setpoint_offset_winter", 0),
            "cascade_time": (
                getattr(settings, "cascade_time", 0) / 60
                if getattr(settings, "cascade_time", 0)
                else 0
            ),
            "wind_chill_avg": getattr(history, "avg_outside_temp", 0),
            "unlock_time": self.get_unlock_time(),
        }

        efficiency = self.calculate_efficiency()
        boiler_status = self.edge_server.get_boiler_status()
        boiler_stats = self.edge_server.get_data_boiler_stats()
        boiler = {
            "status": boiler_status,
            "stats": boiler_stats,
        }
        efficiency["cascade_fire_rate_avg"] = round(
            self.chronos.cascade_fire_rate_avg, 1
        )
        efficiency["hours"] = EFFICIENCY_HOUR
        return {
            **edge_server_data,
            "results": results,
            "efficiency": efficiency,
            "boiler": boiler,
            "devices": devices,
            "status": State.ON.value,
        }

    def get_chart_data(self):
        rows = self.history_repository.get_last_histories()
        data = [
            {
                "column-1": row.water_out_temp,
                "column-2": row.return_temp,
                "date": convert_datetime_to_str(row.timestamp, "%Y-%m-%dT%H:%MZ"),
            }
            for row in reversed(rows)
        ]

        return data

    def three_minute_avg_delta(self):
        data = self.three_minute_avg_delta()
        return data

    def log_generator(self):
        slice_ = 256
        offset = 0
        limit = 256
        stop = False
        log_limit = datetime.now() - timedelta(days=1)
        headers = [
            "LID",
            "logdatetime",
            "outsideTemp",
            "effective_setpoint",
            "waterOutTemp",
            "returnTemp",
            "boilerStatus",
            "cascadeFireRate",
            "leadFireRate",
            "chiller1Status",
            "chiller2Status",
            "chiller3Status",
            "chiller4Status",
            "setPoint2",
            "parameterX_winter",
            "parameterX_summer",
            "t1",
            "MO_B",
            "MO_C1",
            "MO_C2",
            "MO_C3",
            "MO_C4",
            "mode",
            "CCT",
            "windSpeed",
            "avgOutsideTemp",
        ]
        yield ",".join(headers) + "\n"
        while not stop:
            with session_scope() as session:
                rows = (
                    session.query(
                        History.id,
                        History.timestamp,
                        History.outside_temp,
                        History.effective_setpoint,
                        History.water_out_temp,
                        History.return_temp,
                        History.boiler_status,
                        History.cascade_fire_rate,
                        History.lead_fire_rate,
                        History.chiller1_status,
                        History.chiller2_status,
                        History.chiller3_status,
                        History.chiller4_status,
                        History.tha_setpoint,
                        History.setpoint_offset_winter,
                        History.setpoint_offset_summer,
                        History.tolerance,
                        History.boiler_manual_override,
                        History.chiller1_manual_override,
                        History.chiller2_manual_override,
                        History.chiller3_manual_override,
                        History.chiller4_manual_override,
                        History.mode,
                        History.cascade_time,
                        History.wind_speed,
                        History.avg_outside_temp,
                    )
                    .order_by(desc(History.id))
                    .slice(offset, limit)
                    .all()
                )
                session.expunge_all()

            offset += slice_
            limit += slice_
            if rows:
                for row in rows:
                    if row[1] > log_limit:
                        str_row = [
                            (
                                convert_datetime_to_str(row, "%d %b %I:%M %p")
                                if isinstance(row, datetime)
                                else str(row)
                            )
                            for row in row
                        ]
                        yield ",".join(str_row) + "\n"
                    else:
                        stop = True
                        break
            else:
                stop = True

    def calculate_efficiency(self):
        hours = EFFICIENCY_HOUR
        timespan = datetime.now() - timedelta(hours=hours)
        with session_scope() as session:
            amount_minutes = (
                session.query(
                    History.chiller1_status,
                    History.chiller2_status,
                    History.chiller3_status,
                    History.chiller4_status,
                )
                .order_by(desc(History.id))
                .filter(
                    History.mode == 1,
                    History.timestamp > timespan,
                    or_(
                        History.chiller1_status == 1,
                        History.chiller2_status == 1,
                        History.chiller3_status == 1,
                        History.chiller4_status == 1,
                    ),
                )
                .count()
            )
            rows = (
                session.query(History.return_temp, History.effective_setpoint)
                .order_by(desc(History.id))
                .filter(History.timestamp > timespan)
                .subquery()
            )
            effective_setpoint_avg, inlet_temp_avg = session.query(
                func.avg(rows.c.effective_setpoint), func.avg(rows.c.return_temp)
            ).first()

            session.expunge_all()

        effective_setpoint_avg = effective_setpoint_avg or 0
        inlet_temp_avg = inlet_temp_avg or 0
        average_temperature_difference = round(
            inlet_temp_avg - effective_setpoint_avg, 1
        )
        chiller_efficiency = round(amount_minutes / float(4 * 60 * hours), 1)
        return {
            "average_temperature_difference": average_temperature_difference,
            "chillers_efficiency": chiller_efficiency,
        }

    def keep_history_for_last_week(self):
        with session_scope() as session:
            old_history = session.query(History).filter(
                History.timestamp < (datetime.now() - timedelta(days=7))
            )
            old_history.delete()

            session.expunge_all()

    def get_boiler_stats(self):
        return self.edge_server.get_data_boiler_stats()

    def update_settings(self, data):
        mode = self.setting_repository._get_property_from_db("mode")
        if mode == 0:
            point = data.setpoint_offset_winter
        else:
            point = data.setpoint_offset_summer

        reponse = self.edge_server.boiler_set_setpoint(point)
        for key, value in data.dict().items():
            if value is not None:
                setattr(self.chronos, key, value)
        return reponse

    def boiler_set_setpoint(self, temperature: float):
        limits = self.edge_server.get_temperature_limits()
        hard_limits = limits["hard_limits"]
        soft_limits = limits["soft_limits"]
        if (
            temperature < hard_limits["min_setpoint"]
            or temperature > hard_limits["max_setpoint"]
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Temperature must be between {hard_limits['min_setpoint']}°F and {hard_limits['max_setpoint']}°F",
            )
        if (
            temperature < soft_limits["min_setpoint"]
            or temperature > soft_limits["max_setpoint"]
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Temperature must be between {soft_limits['min_setpoint']}°F and {soft_limits['max_setpoint']}°F",
            )
        return self.edge_server.boiler_set_setpoint(temperature)

    def switch_season_mode(self, season_value: int):
        """
        Args:
            season_value (int): The season value to switch to. SUMMER (0) or WINTER (1)
        Step to switch seasion:
        1. Change mode to WAITING_SWITCH_TO_WINTER or WAITING_SWITCH_TO_SUMMER:
            - Turn off all devices
            - Turn on/off valves (summer or winter)
            - Add job to switch season after <mode_switch_lockout_time> minutes. <mode_switch_lockout_time> will be set in user's setting
        2. Run the job to switch season after <mode_switch_lockout_time> minutes:
            - Restore devices states
            - Switch devices
            - Change mode to SUMMER or WINTER
        """

        if season_value not in [Mode.WINTER.value, Mode.SUMMER.value]:
            raise HTTPException(
                status_code=400, detail=f"Invalid season value: {season_value}"
            )

        waiting_mode = (
            Mode.WAITING_SWITCH_TO_WINTER
            if season_value == Mode.WINTER.value
            else Mode.WAITING_SWITCH_TO_SUMMER
        )
        self.chronos._switch_season(waiting_mode.value)

        settings = self.setting_repository.get_last_settings()
        unlock_time = get_current_time(UTC) + timedelta(
            minutes=settings.mode_switch_lockout_time
        )

        return {
            "status": "success",
            "mode": season_value,
            "mode_switch_lockout_time": self.chronos.mode_switch_lockout_time,
            "unlock_time": unlock_time.isoformat(),
        }

    def get_switch_timestamp(self, id: int):
        device = self._get_device(id)
        return device.switched_timestamp if device else None

    def update_device_state(self, data):
        try:
            device_state = self.edge_server.update_device_state(
                id=data.id, state=data.state
            )
            self.update_device_state_in_db(id=data.id, state=data.state)
            return device_state
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update device state: {str(e)}"
            )

    def update_device_state_in_db(self, id: int, state: bool):
        if device := self._get_device(id):
            device.status = 1 if state else 0
            device.switched_timestamp = get_current_time(UTC)

    def get_unlock_time(self):
        mode_switch_timestamp = self.setting_repository._get_property_from_db(
            "mode_switch_timestamp"
        )
        lockout_time = self.setting_repository._get_property_from_db(
            "mode_switch_lockout_time"
        )
        unlock_time = mode_switch_timestamp + timedelta(minutes=lockout_time)
        return convert_datetime_to_str(unlock_time, "%Y-%m-%dT%H:%M:%SZ")
