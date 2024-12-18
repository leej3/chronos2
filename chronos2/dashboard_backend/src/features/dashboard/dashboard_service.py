import os
from datetime import datetime, timedelta
from src.core.chronos import Chronos
from src.core.utils.config_parser import cfg
from src.core.repositories.history_repository import HistoryRepository
from src.core.repositories.setting_repository import SettingRepository
from src.core.models import History
from src.core.configs.database import session_scope
from sqlalchemy import desc, or_
from sqlalchemy.sql import func


class DashboardService:
    def __init__(self):
        self.chronos = Chronos()
        self.history_repository = HistoryRepository()
        self.setting_repository = SettingRepository()

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

    def get_data(self):
        history = self.history_repository.get_last_history()
        settings = self.setting_repository.get_last_settings()

        results = {
            "outside_temp": history.outside_temp if history else 0,
            "baseline_setpoint": self.chronos.baseline_setpoint,
            "tha_setpoint": history.tha_setpoint if history else 0,
            "effective_setpoint": history.effective_setpoint if history else 0,
            "tolerance": settings.tolerance if settings else 0,
            "setpoint_min": settings.setpoint_min if settings else 0,
            "setpoint_max": settings.setpoint_max if settings else 0,
            "mode_change_delta_temp": (
                settings.mode_change_delta_temp if settings else 0
            ),
            "mode_switch_lockout_time": (
                settings.mode_switch_lockout_time if settings else 0
            ),
            # TODO: get data from edge_server
            # "return_temp": self.chronos.return_temp,
            # "water_out_temp": self.chronos.water_out_temp,
            "mode": settings.mode if settings else 0,
            "setpoint_offset_summer": (
                settings.setpoint_offset_summer if settings else 0
            ),
            "setpoint_offset_winter": (
                settings.setpoint_offset_winter if settings else 0
            ),
            "cascade_time": settings.cascade_time / 60 if settings else 0,
            "wind_chill_avg": history.avg_outside_temp if history else 0,
        }
        efficiency = self.calculate_efficiency()
        efficiency["cascade_fire_rate_avg"] = round(
            self.chronos.cascade_fire_rate_avg, 1
        )
        efficiency["hours"] = cfg.efficiency.hours
        # actStream = [
        #     {
        #         "timeStamp": device.switched_timestamp.strftime("%B %d, %I:%M %p"),
        #         "status": device.status,
        #         "MO": device.manual_override,
        #     }
        #     for device in self.chronos.devices
        # ]
        return {
            "results": results,
            # "actStream": actStream,
            # "chronos_status": self.get_chronos_status(),
            "efficiency": efficiency,
        }

    def get_chart_data(self):
        rows = self.history_repository.get_last_histories()
        data = [
            {
                "column-1": row.water_out_temp,
                "column-2": row.return_temp,
                "date": row.timestamp.strftime("%Y-%m-%d %H:%M"),
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
                                row.strftime("%d %b %I:%M %p")
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
        hours = cfg.efficiency.hours
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
